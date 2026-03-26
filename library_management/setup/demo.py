from __future__ import annotations

import frappe
from frappe.utils import add_days, today

from library_management.services.circulation import issue_copy, return_copy
from library_management.services.member import refresh_member_counters
from library_management.services.reservation import place_reservation


def _ensure_settings(mode="Hybrid"):
    if not frappe.db.exists("DocType", "Library Settings"):
        return
    settings = frappe.get_single("Library Settings")
    settings.library_name = settings.library_name or "Sahil Central Library"
    settings.library_mode = mode
    settings.save(ignore_permissions=True)


def _ensure_item(item_code, item_name, **library_fields):
    if frappe.db.exists("Item", item_code):
        return frappe.get_doc("Item", item_code)
    doc = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_name,
            "item_group": "Library Materials" if frappe.db.exists("Item Group", "Library Materials") else "All Item Groups",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            **library_fields,
        }
    ).insert(ignore_permissions=True)
    return doc


def _ensure_copy(item, accession_no, barcode, shelf=None):
    existing = frappe.db.get_value("Library Copy", {"accession_no": accession_no}, "name")
    if existing:
        return existing
    return frappe.get_doc(
        {
            "doctype": "Library Copy",
            "item": item,
            "accession_no": accession_no,
            "barcode": barcode,
            "status": "Available",
            "shelf": shelf,
        }
    ).insert(ignore_permissions=True).name


@frappe.whitelist()
def create_school_demo_data():
    _ensure_settings("School")
    shelf = _ensure_shelf("SCH-A-01", "Academic Block", "Reference")
    item1 = _ensure_item("LIB-BOOK-001", "Introduction to Physics", library_material_type="Book", library_authors="Halliday", library_isbn_13="9780000000001")
    item2 = _ensure_item("LIB-BOOK-002", "Modern Indian History", library_material_type="Book", library_authors="Bipan Chandra", library_isbn_13="9780000000002")
    _ensure_copy(item1.name, "SCH-ACC-001", "SCH-BC-001", shelf)
    _ensure_copy(item1.name, "SCH-ACC-002", "SCH-BC-002", shelf)
    _ensure_copy(item2.name, "SCH-ACC-003", "SCH-BC-003", shelf)
    _ensure_member("Student Demo", "Student", member_card_no="STD-001")
    _ensure_member("Teacher Demo", "Teacher", member_card_no="TCH-001")


@frappe.whitelist()
def create_public_library_demo_data():
    _ensure_settings("Independent")
    shelf = _ensure_shelf("PUB-A-01", "Public Wing", "Circulation")
    plan = _ensure_plan("Annual Public Membership")
    item1 = _ensure_item("LIB-PUB-001", "The Pragmatic Programmer", library_material_type="Book", library_authors="Andrew Hunt", library_isbn_13="9780000000003")
    item2 = _ensure_item("LIB-PUB-002", "Clean Architecture", library_material_type="Book", library_authors="Robert C. Martin", library_isbn_13="9780000000004")
    _ensure_copy(item1.name, "PUB-ACC-001", "PUB-BC-001", shelf)
    _ensure_copy(item2.name, "PUB-ACC-002", "PUB-BC-002", shelf)
    _ensure_member("Public Member Demo", "Public Member", member_card_no="PUB-001", membership_plan=plan)


def _ensure_plan(plan_name):
    if frappe.db.exists("Library Membership Plan", plan_name):
        return plan_name
    frappe.get_doc(
        {
            "doctype": "Library Membership Plan",
            "plan_name": plan_name,
            "is_paid_membership": 1,
            "fee_amount": 500,
            "deposit_amount": 1000,
            "validity_days": 365,
            "default_member_category": "Public Member",
        }
    ).insert(ignore_permissions=True)
    return plan_name


def _ensure_shelf(code, branch, section):
    if frappe.db.exists("Library Shelf", code):
        return code
    frappe.get_doc(
        {
            "doctype": "Library Shelf",
            "shelf_code": code,
            "branch": branch,
            "section_name": section,
            "shelf_label": code,
        }
    ).insert(ignore_permissions=True)
    return code


def _ensure_member(member_name, category, **extra):
    existing = frappe.db.get_value("Library Member", {"member_name": member_name}, "name")
    if existing:
        return existing
    doc = frappe.get_doc(
        {
            "doctype": "Library Member",
            "member_name": member_name,
            "member_category": category,
            "status": "Active",
            "validity_start_date": today(),
            "validity_end_date": add_days(today(), 365),
            **extra,
        }
    ).insert(ignore_permissions=True)
    return doc.name


@frappe.whitelist()
def create_activity_demo_data():
    _ensure_settings("Hybrid")
    _purge_existing_activity_demo_data()

    shelf_a = _ensure_shelf("DEMO-A-01", "Main Library", "Circulation")
    shelf_b = _ensure_shelf("DEMO-B-01", "Main Library", "Reference")

    items = [
        _ensure_item(
            "LIB-DEMO-001",
            "Data Structures and Algorithms",
            library_material_type="Book",
            library_authors="Narasimha Karumanchi",
            library_isbn_13="9789351194683",
        ),
        _ensure_item(
            "LIB-DEMO-002",
            "Database System Concepts",
            library_material_type="Book",
            library_authors="Silberschatz, Korth",
            library_isbn_13="9789332575777",
        ),
        _ensure_item(
            "LIB-DEMO-003",
            "Operating System Concepts",
            library_material_type="Book",
            library_authors="Abraham Silberschatz",
            library_isbn_13="9781119800368",
        ),
        _ensure_item(
            "LIB-DEMO-004",
            "Clean Code",
            library_material_type="Book",
            library_authors="Robert C. Martin",
            library_isbn_13="9780132350884",
        ),
        _ensure_item(
            "LIB-DEMO-005",
            "Introduction to Psychology",
            library_material_type="Book",
            library_authors="Morgan and King",
            library_isbn_13="9780000000105",
        ),
        _ensure_item(
            "LIB-DEMO-006",
            "Research Methodology Handbook",
            library_material_type="Reference Material",
            library_authors="Kothari",
            library_is_reference_only=1,
            library_is_borrowable=0,
            library_isbn_13="9780000000106",
        ),
    ]

    copies = {
        "copy_1": _ensure_copy(items[0].name, "DEMO-ACC-001", "DEMO-BC-001", shelf_a),
        "copy_2": _ensure_copy(items[0].name, "DEMO-ACC-002", "DEMO-BC-002", shelf_a),
        "copy_3": _ensure_copy(items[1].name, "DEMO-ACC-003", "DEMO-BC-003", shelf_a),
        "copy_4": _ensure_copy(items[2].name, "DEMO-ACC-004", "DEMO-BC-004", shelf_a),
        "copy_5": _ensure_copy(items[3].name, "DEMO-ACC-005", "DEMO-BC-005", shelf_a),
        "copy_6": _ensure_copy(items[4].name, "DEMO-ACC-006", "DEMO-BC-006", shelf_a),
        "copy_7": _ensure_copy(items[5].name, "DEMO-ACC-007", "DEMO-BC-007", shelf_b),
    }

    members = {
        "student_1": _ensure_member("Aarav Sharma", "Student", member_card_no="STD-DEMO-001"),
        "student_2": _ensure_member("Diya Patel", "Student", member_card_no="STD-DEMO-002"),
        "teacher_1": _ensure_member("Prof. Meera Iyer", "Teacher", member_card_no="TCH-DEMO-001"),
        "staff_1": _ensure_member("Rohan Nair", "Staff", member_card_no="STF-DEMO-001"),
        "public_1": _ensure_member("Neha Verma", "Public Member", member_card_no="PUB-DEMO-001"),
    }

    transaction_names = []
    reservation_names = []
    fine_names = []

    events = [
        {"member": members["student_1"], "copy": copies["copy_1"], "issue_days_ago": 28, "return_days_ago": 20},
        {"member": members["student_2"], "copy": copies["copy_3"], "issue_days_ago": 26, "return_days_ago": 9},
        {"member": members["teacher_1"], "copy": copies["copy_4"], "issue_days_ago": 24, "return_days_ago": 5},
        {"member": members["staff_1"], "copy": copies["copy_5"], "issue_days_ago": 22, "return_days_ago": 15},
        {"member": members["public_1"], "copy": copies["copy_6"], "issue_days_ago": 19, "return_days_ago": 3},
        {"member": members["student_1"], "copy": copies["copy_2"], "issue_days_ago": 17, "return_days_ago": 2},
        {"member": members["teacher_1"], "copy": copies["copy_1"], "issue_days_ago": 14, "return_days_ago": None},
        {"member": members["staff_1"], "copy": copies["copy_3"], "issue_days_ago": 12, "return_days_ago": None},
        {"member": members["student_2"], "copy": copies["copy_4"], "issue_days_ago": 10, "return_days_ago": 1, "condition": "Damaged"},
        {"member": members["public_1"], "copy": copies["copy_5"], "issue_days_ago": 8, "return_days_ago": None},
        {"member": members["student_1"], "copy": copies["copy_6"], "issue_days_ago": 6, "return_days_ago": None},
        {"member": members["teacher_1"], "copy": copies["copy_2"], "issue_days_ago": 4, "return_days_ago": None},
    ]

    for index, event in enumerate(events, start=1):
        issue_date = add_days(today(), -event["issue_days_ago"])
        copy_name = event["copy"]

        _reset_demo_copy(copy_name)
        transaction = issue_copy(event["member"], copy_name, issue_date=issue_date)
        transaction_key = transaction.name

        if event.get("return_days_ago") is not None:
            return_date = add_days(today(), -event["return_days_ago"])
            transaction = return_copy(
                copy_name,
                condition_status=event.get("condition", "Good"),
                return_date=return_date,
            )
            transaction_key = transaction.name

        transaction_names.append(transaction_key)
        if frappe.db.get_value("Library Transaction", transaction_key, "fine"):
            fine_names.append(frappe.db.get_value("Library Transaction", transaction_key, "fine"))

    reservation_data = [
        {"member": members["public_1"], "item": items[0].name},
        {"member": members["student_2"], "item": items[0].name},
        {"member": members["staff_1"], "item": items[3].name},
    ]
    for row in reservation_data:
        existing = frappe.db.get_value(
            "Library Reservation",
            {"member": row["member"], "item": row["item"], "status": ["in", ["Pending", "Ready for Pickup"]]},
            "name",
        )
        if existing:
            reservation_names.append(existing)
            continue
        reservation = place_reservation(row["member"], row["item"])
        reservation_names.append(reservation.name)

    for member in members.values():
        refresh_member_counters(member)

    return {
        "members": list(members.values()),
        "items": [item.name for item in items],
        "transactions": transaction_names,
        "reservations": reservation_names,
        "fines": fine_names,
    }


@frappe.whitelist()
def create_copy_model_demo_data():
    _ensure_settings("Hybrid")
    _purge_copy_model_demo_data()

    shelf = _ensure_shelf("COPY-DEMO-01", "Main Library", "Circulation")
    item = _ensure_item(
        "LIB-COPY-DEMO-001",
        "Python Fundamentals - Copy Model Demo",
        library_material_type="Book",
        library_authors="Demo Author",
        library_isbn_13="9780000099001",
    )

    member = _ensure_member("Copy Model Demo Member", "Student", member_card_no="COPY-DEMO-001")

    copies = {
        "available": _ensure_copy(item.name, "COPY-ACC-001", "COPY-BC-001", shelf),
        "issued": _ensure_copy(item.name, "COPY-ACC-002", "COPY-BC-002", shelf),
        "repair": _ensure_copy(item.name, "COPY-ACC-003", "COPY-BC-003", shelf),
    }

    for copy_name in copies.values():
        _reset_demo_copy(copy_name)

    issue_copy(member, copies["issued"], issue_date=add_days(today(), -3))

    frappe.db.set_value(
        "Library Copy",
        copies["repair"],
        {
            "status": "Under Repair",
            "condition_status": "Damaged",
            "current_member": None,
        },
        update_modified=False,
    )

    refresh_member_counters(member)

    return {
        "item": item.name,
        "member": member,
        "copies": {
            "available": copies["available"],
            "issued": copies["issued"],
            "repair": copies["repair"],
        },
    }


def _purge_existing_activity_demo_data():
    reservation_names = frappe.get_all(
        "Library Reservation",
        filters={"name": ["like", "LIB-RES-%"]},
        pluck="name",
    )
    for name in reservation_names:
        member = frappe.db.get_value("Library Reservation", name, "member")
        if member and frappe.db.get_value("Library Member", member, "member_card_no") in {
            "STD-DEMO-001",
            "STD-DEMO-002",
            "TCH-DEMO-001",
            "STF-DEMO-001",
            "PUB-DEMO-001",
        }:
            frappe.delete_doc("Library Reservation", name, ignore_permissions=True, force=1)

    demo_copies = set(
        frappe.get_all(
            "Library Copy",
            filters={"accession_no": ["like", "DEMO-ACC-%"]},
            pluck="name",
        )
    )
    if demo_copies:
        for name in frappe.get_all(
            "Library Transaction",
            filters={"copy": ["in", list(demo_copies)]},
            pluck="name",
        ):
            fine = frappe.db.get_value("Library Transaction", name, "fine")
            if fine and frappe.db.exists("Library Fine", fine):
                frappe.delete_doc("Library Fine", fine, ignore_permissions=True, force=1)
            frappe.delete_doc("Library Transaction", name, ignore_permissions=True, force=1)

        for name in frappe.get_all(
            "Library Fine",
            filters={"copy": ["in", list(demo_copies)]},
            pluck="name",
        ):
            frappe.delete_doc("Library Fine", name, ignore_permissions=True, force=1)

    for copy_name in demo_copies:
        _reset_demo_copy(copy_name)


def _purge_copy_model_demo_data():
    demo_copies = set(
        frappe.get_all(
            "Library Copy",
            filters={"accession_no": ["like", "COPY-ACC-%"]},
            pluck="name",
        )
    )

    if demo_copies:
        for name in frappe.get_all(
            "Library Transaction",
            filters={"copy": ["in", list(demo_copies)]},
            pluck="name",
        ):
            fine = frappe.db.get_value("Library Transaction", name, "fine")
            if fine and frappe.db.exists("Library Fine", fine):
                frappe.delete_doc("Library Fine", fine, ignore_permissions=True, force=1)
            frappe.delete_doc("Library Transaction", name, ignore_permissions=True, force=1)

    for copy_name in demo_copies:
        _reset_demo_copy(copy_name)


def _reset_demo_copy(copy_name):
    frappe.db.set_value(
        "Library Copy",
        copy_name,
        {
            "status": "Available",
            "current_member": None,
            "condition_status": "Good",
            "is_borrowable": 1,
            "is_reference_only": 0,
        },
        update_modified=False,
    )
