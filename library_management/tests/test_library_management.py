import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from library_management.services.circulation import issue_copy, renew_transaction, return_copy
from library_management.services.member import refresh_member_counters
from library_management.services.reservation import place_reservation


class TestLibraryManagement(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = frappe.get_single("Library Settings")
        cls.settings.library_name = "Test Library"
        cls.settings.save(ignore_permissions=True)

    def setUp(self):
        self.item = self._ensure_item("TEST-LIB-ITEM", "Test Library Book")
        self.copy = self._ensure_copy(self.item, "TEST-ACC-001", "TEST-BC-001")
        self.student = self._ensure_member("Test Student", "Student")
        self.teacher = self._ensure_member("Test Teacher", "Teacher")

    def test_issue_flow(self):
        txn = issue_copy(self.student, self.copy)
        self.assertEqual(txn.status, "Issued")
        self.assertEqual(frappe.db.get_value("Library Copy", self.copy, "status"), "Issued")

    def test_return_flow_and_fine(self):
        txn = issue_copy(self.student, self.copy)
        frappe.db.set_value("Library Transaction", txn.name, "due_date", add_days(today(), -5), update_modified=False)
        returned = return_copy(self.copy)
        self.assertEqual(returned.status, "Returned")
        self.assertGreaterEqual(returned.overdue_days, 1)

    def test_renewal_restriction_when_reserved(self):
        txn = issue_copy(self.student, self.copy)
        place_reservation(self.teacher, self.item)
        with self.assertRaises(frappe.ValidationError):
            renew_transaction(txn.name)

    def test_reference_only_cannot_issue(self):
        frappe.db.set_value("Library Copy", self.copy, {"is_reference_only": 1, "status": "Reference Only"}, update_modified=False)
        with self.assertRaises(frappe.ValidationError):
            issue_copy(self.student, self.copy)

    def test_reservation_queue(self):
        place_reservation(self.student, self.item)
        second = place_reservation(self.teacher, self.item)
        self.assertEqual(second.queue_position, 2)

    def test_lost_item_handling(self):
        txn = issue_copy(self.student, self.copy)
        lost = return_copy(self.copy, mark_lost=True)
        self.assertEqual(lost.status, "Lost")
        self.assertEqual(frappe.db.get_value("Library Copy", self.copy, "status"), "Lost")

    def test_expired_member_cannot_issue(self):
        frappe.db.set_value("Library Member", self.student, {"validity_end_date": add_days(today(), -1), "status": "Expired"}, update_modified=False)
        with self.assertRaises(frappe.ValidationError):
            issue_copy(self.student, self.copy)

    def _ensure_item(self, item_code, item_name):
        existing = frappe.db.exists("Item", item_code)
        if existing:
            return item_code
        return frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_name,
                "item_group": "Library Materials" if frappe.db.exists("Item Group", "Library Materials") else "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "library_material_type": "Book",
                "library_is_borrowable": 1,
            }
        ).insert(ignore_permissions=True).name

    def _ensure_copy(self, item, accession_no, barcode):
        existing = frappe.db.get_value("Library Copy", {"accession_no": accession_no}, "name")
        if existing:
            frappe.db.set_value("Library Copy", existing, {"status": "Available", "current_member": None, "is_borrowable": 1, "is_reference_only": 0}, update_modified=False)
            return existing
        return frappe.get_doc(
            {
                "doctype": "Library Copy",
                "item": item,
                "accession_no": accession_no,
                "barcode": barcode,
                "status": "Available",
                "is_borrowable": 1,
            }
        ).insert(ignore_permissions=True).name

    def _ensure_member(self, member_name, category):
        existing = frappe.db.get_value("Library Member", {"member_name": member_name}, "name")
        if existing:
            frappe.db.set_value(
                "Library Member",
                existing,
                {"status": "Active", "validity_start_date": today(), "validity_end_date": add_days(today(), 365)},
                update_modified=False,
            )
            refresh_member_counters(existing)
            return existing
        return frappe.get_doc(
            {
                "doctype": "Library Member",
                "member_name": member_name,
                "member_category": category,
                "status": "Active",
                "validity_start_date": today(),
                "validity_end_date": add_days(today(), 365),
            }
        ).insert(ignore_permissions=True).name
