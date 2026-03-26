from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate, now_datetime, today

from library_management.services.member import validate_member_for_issue
from library_management.utils import get_library_settings


def reorder_queue(item: str, copy: str | None = None):
    filters = {"status": ["in", ["Pending", "Ready for Pickup"]], "item": item}
    if copy:
        filters["copy"] = copy

    reservations = frappe.get_all(
        "Library Reservation",
        filters=filters,
        fields=["name"],
        order_by="priority desc, creation asc",
    )
    for idx, row in enumerate(reservations, start=1):
        frappe.db.set_value("Library Reservation", row.name, "queue_position", idx, update_modified=False)


def place_reservation(member: str, item: str, copy: str | None = None, notes: str | None = None):
    validate_member_for_issue(member)

    reservation = frappe.get_doc(
        {
            "doctype": "Library Reservation",
            "member": member,
            "item": item,
            "copy": copy,
            "reservation_date": today(),
            "status": "Pending",
            "notes": notes,
        }
    ).insert(ignore_permissions=True)
    reorder_queue(item, copy)
    reservation.reload()
    return reservation


def allocate_next_reservation(item: str, copy: str | None = None):
    settings = get_library_settings()
    filters = {"item": item, "status": "Pending"}
    if copy:
        filters["copy"] = ["in", [copy, "", None]]
    reservation_name = frappe.get_all("Library Reservation", filters=filters, order_by="priority desc, creation asc", pluck="name", limit=1)
    if not reservation_name:
        return None

    reservation = frappe.get_doc("Library Reservation", reservation_name[0])
    hold_days = settings.hold_expiry_days or 2
    reservation.status = "Ready for Pickup"
    reservation.ready_on = today()
    reservation.expires_on = add_days(today(), hold_days)
    if copy:
        reservation.copy = copy
    reservation.save(ignore_permissions=True)

    if copy:
        frappe.db.set_value("Library Copy", copy, "status", "Reserved", update_modified=False)

    reorder_queue(item, copy)
    return reservation


def fulfill_reservation(reservation_name: str, transaction_name: str):
    reservation = frappe.get_doc("Library Reservation", reservation_name)
    reservation.status = "Fulfilled"
    reservation.fulfilled_on = today()
    reservation.transaction = transaction_name
    reservation.save(ignore_permissions=True)
    reorder_queue(reservation.item, reservation.copy)


def cancel_reservation(reservation_name: str):
    reservation = frappe.get_doc("Library Reservation", reservation_name)
    reservation.status = "Cancelled"
    reservation.save(ignore_permissions=True)
    reorder_queue(reservation.item, reservation.copy)


def expire_stale_reservations():
    expired = frappe.get_all(
        "Library Reservation",
        filters={"status": "Ready for Pickup", "expires_on": ["<", getdate(today())]},
        pluck="name",
    )
    for name in expired:
        reservation = frappe.get_doc("Library Reservation", name)
        reservation.status = "Expired"
        reservation.save(ignore_permissions=True)
        if reservation.copy:
            frappe.db.set_value("Library Copy", reservation.copy, "status", "Available", update_modified=False)
            allocate_next_reservation(reservation.item, reservation.copy)
        else:
            allocate_next_reservation(reservation.item)
        reorder_queue(reservation.item, reservation.copy)
