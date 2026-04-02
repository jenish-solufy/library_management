import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import today

from library_management.services.reservation import reorder_queue


class LibraryReservation(Document):
    def autoname(self):
        if not self.name or self.name.startswith("New Library Reservation"):
            self.name = make_autoname("LIB-RES-.YYYY.-.#####")

    def validate(self):
        if not self.reservation_date:
            self.reservation_date = today()
        if self.copy and not self.item:
            self.item = frappe.db.get_value("Library Copy", self.copy, "item")
        if not self.item:
            frappe.throw("Item is required for a reservation.")
        if self.copy:
            copy_status = frappe.db.get_value("Library Copy", self.copy, "status")
            if copy_status == "Withdrawn":
                frappe.throw("Withdrawn copies cannot be reserved.")
        self.validate_duplicate_open_reservation()

    def after_insert(self):
        reorder_queue(self.item, self.copy)

    def on_update(self):
        reorder_queue(self.item, self.copy)

    def validate_duplicate_open_reservation(self):
        filters = {
            "member": self.member,
            "item": self.item,
            "status": ["in", ["Pending", "Ready for Pickup"]],
            "name": ["!=", self.name],
        }
        if self.copy:
            filters["copy"] = self.copy
        if frappe.db.exists("Library Reservation", filters):
            frappe.throw("An active reservation already exists for this member and title.")
