from __future__ import annotations

import frappe
from frappe.utils import cint, flt, getdate, now_datetime, today

from library_management.services.fine import calculate_overdue_fine, create_or_update_fine
from library_management.services.member import refresh_member_counters, validate_member_for_issue
from library_management.services.reservation import allocate_next_reservation, fulfill_reservation
from library_management.utils import get_due_date, get_library_settings, get_member_policy


def _lock_copy(copy_name: str):
    rows = frappe.db.sql(
        """
        select name, item, status, condition_status, is_reference_only, is_borrowable
        from `tabLibrary Copy`
        where name = %s
        for update
        """,
        copy_name,
        as_dict=True,
    )
    if not rows:
        frappe.throw(f"Library Copy {copy_name} not found.")
    return frappe._dict(rows[0])


def _get_copy_by_scan(scan_value: str):
    for fieldname in ("name", "barcode", "accession_no"):
        name = frappe.db.get_value("Library Copy", {fieldname: scan_value}, "name")
        if name:
            return name
    frappe.throw(f"No library copy found for {scan_value}.")


def get_available_copy_for_item(item: str):
    copy_name = frappe.db.get_value(
        "Library Copy",
        {"item": item, "status": "Available", "is_borrowable": 1},
        "name",
        order_by="modified asc",
    )
    if copy_name:
        return copy_name

    copy_name = frappe.db.get_value("Library Copy", {"item": item}, "name", order_by="modified asc")
    if copy_name:
        return copy_name

    frappe.throw(f"No library copies found for item {item}.")


def issue_copy(member_name: str, copy_name: str, issue_date=None, reservation_name: str | None = None):
    issue_date = getdate(issue_date or today())
    member = validate_member_for_issue(member_name)
    policy = get_member_policy(member.member_category)
    if cint(member.current_issued_count) >= cint(policy.max_books):
        frappe.throw(f"Borrowing limit exceeded for member category {member.member_category}.")

    copy = _lock_copy(copy_name)
    if copy.status != "Available":
        frappe.throw(f"Copy {copy_name} is currently {copy.status}.")
    if cint(copy.is_reference_only) or not cint(copy.is_borrowable):
        frappe.throw("This copy is not borrowable.")

    item = frappe.get_doc("Item", copy.item)
    if cint(item.library_is_reference_only) or not cint(item.library_is_borrowable):
        frappe.throw("This title is not borrowable.")

    waiting_reservation = frappe.db.exists(
        "Library Reservation",
        {"item": copy.item, "status": "Ready for Pickup", "copy": ["in", [copy_name, "", None]]},
    )
    if waiting_reservation and waiting_reservation != reservation_name:
        reservation = frappe.get_doc("Library Reservation", waiting_reservation)
        if reservation.member != member_name:
            frappe.throw("This copy is reserved for another member.")

    due_date = get_due_date(issue_date, member.member_category, copy.item)

    transaction = frappe.get_doc(
        {
            "doctype": "Library Transaction",
            "transaction_type": "Issue",
            "member": member_name,
            "item": copy.item,
            "copy": copy_name,
            "issue_date": issue_date,
            "due_date": due_date,
            "status": "Issued",
            "company": get_library_settings().company,
        }
    ).insert(ignore_permissions=True)

    frappe.db.set_value(
        "Library Copy",
        copy_name,
        {"status": "Issued", "current_member": member_name, "last_issue_date": issue_date},
        update_modified=False,
    )

    if reservation_name:
        fulfill_reservation(reservation_name, transaction.name)

    refresh_member_counters(member_name)
    return transaction


def issue_by_scan(member_name: str, scan_value: str, reservation_name: str | None = None):
    copy_name = _get_copy_by_scan(scan_value)
    return issue_copy(member_name, copy_name, reservation_name=reservation_name)


def issue_by_item(member_name: str, item: str, reservation_name: str | None = None):
    copy_name = get_available_copy_for_item(item)
    return issue_copy(member_name, copy_name, reservation_name=reservation_name)


def renew_transaction(transaction_name: str, renewal_date=None):
    renewal_date = getdate(renewal_date or today())
    transaction = frappe.get_doc("Library Transaction", transaction_name)
    if transaction.status not in {"Issued", "Overdue"}:
        frappe.throw("Only active loans can be renewed.")

    policy = get_member_policy(transaction.member_category or frappe.db.get_value("Library Member", transaction.member, "member_category"))
    if cint(transaction.renewal_count) >= cint(policy.max_renewals):
        frappe.throw("Maximum renewals reached for this transaction.")

    waiting = frappe.db.exists(
        "Library Reservation",
        {"item": transaction.item, "status": ["in", ["Pending", "Ready for Pickup"]], "member": ["!=", transaction.member]},
    )
    if waiting:
        frappe.throw("Renewal is blocked because another member is waiting for this title.")

    transaction.renewal_count = cint(transaction.renewal_count) + 1
    transaction.transaction_type = "Renew"
    transaction.last_renewal_date = renewal_date
    transaction.due_date = get_due_date(renewal_date, transaction.member_category, transaction.item)
    transaction.status = "Issued"
    transaction.save(ignore_permissions=True)
    refresh_member_counters(transaction.member)
    return transaction


def return_copy(scan_value: str, condition_status="Good", return_date=None, mark_lost=False, notes=None):
    return_date = getdate(return_date or today())
    copy_name = _get_copy_by_scan(scan_value)
    copy = _lock_copy(copy_name)
    transaction_name = frappe.db.get_value(
        "Library Transaction",
        {"copy": copy_name, "status": ["in", ["Issued", "Overdue"]]},
        "name",
    )
    if not transaction_name:
        frappe.throw("No active loan found for this copy.")

    transaction = frappe.get_doc("Library Transaction", transaction_name)
    settings = get_library_settings()
    transaction.return_date = return_date
    transaction.notes = notes
    transaction.condition_on_return = condition_status
    transaction.overdue_days, overdue_fine = calculate_overdue_fine(transaction.member_category, transaction.due_date, return_date)

    copy_status = "Available"
    charge_type = "Overdue"
    fine_amount = overdue_fine

    if mark_lost:
        transaction.status = "Lost"
        transaction.transaction_type = "Lost"
        copy_status = "Lost"
        charge_type = "Lost"
        fine_amount = flt(transaction.valuation_rate) * flt(settings.default_lost_item_multiplier or 1)
    elif condition_status == "Damaged":
        transaction.status = "Damaged"
        transaction.transaction_type = "Return"
        copy_status = "Under Repair"
        fine_amount += flt(settings.default_damage_fee or 0)
        charge_type = "Damaged"
    else:
        transaction.status = "Returned"
        transaction.transaction_type = "Return"

    transaction.save(ignore_permissions=True)
    fine = create_or_update_fine(transaction, charge_type=charge_type, amount=fine_amount, description=notes)
    if fine:
        transaction.db_set("fine", fine.name, update_modified=False)

    frappe.db.set_value(
        "Library Copy",
        copy_name,
        {
            "status": copy_status,
            "condition_status": condition_status if not mark_lost else "Lost",
            "current_member": None,
            "last_return_date": return_date,
        },
        update_modified=False,
    )

    if copy_status == "Available":
        allocate_next_reservation(transaction.item, copy_name)

    refresh_member_counters(transaction.member)
    return transaction


def refresh_overdues():
    rows = frappe.get_all(
        "Library Transaction",
        filters={"status": "Issued", "due_date": ["<", getdate(today())]},
        fields=["name", "member_category", "due_date"],
    )
    for row in rows:
        overdue_days, amount = calculate_overdue_fine(row.member_category, row.due_date)
        frappe.db.set_value(
            "Library Transaction",
            row.name,
            {"status": "Overdue", "overdue_days": overdue_days},
            update_modified=False,
        )
