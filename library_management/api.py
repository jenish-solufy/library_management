from __future__ import annotations

import frappe

from library_management.services.circulation import (
    get_available_copy_for_item,
    issue_by_item,
    issue_by_scan,
    renew_transaction,
    return_copy,
)
from library_management.services.reservation import place_reservation
from library_management.utils import get_item_availability


def _get_copy_payload(copy_name: str):
    copy = frappe.db.get_value(
        "Library Copy",
        copy_name,
        ["name", "item", "accession_no", "barcode", "status", "current_member", "condition_status"],
        as_dict=True,
    )
    item = frappe.db.get_value(
        "Item",
        copy.item,
        ["name", "item_name", "library_authors", "library_material_type", "library_front_cover", "library_back_cover"],
        as_dict=True,
    )
    return {"copy": copy, "item": item, "availability": get_item_availability(copy.item)}


def _get_member_payload(member_name: str | None):
    if not member_name:
        return None
    return frappe.db.get_value(
        "Library Member",
        member_name,
        ["name", "member_name", "member_category", "status", "current_issued_count", "outstanding_fines"],
        as_dict=True,
    )


@frappe.whitelist()
def get_library_member_context(member: str):
    member_payload = _get_member_payload(member)
    if not member_payload:
        frappe.throw("Library Member not found.")
    return {"member": member_payload}


@frappe.whitelist()
def barcode_lookup(scan_value: str = "", item: str | None = None, member: str | None = None):
    copy_name = None
    if scan_value:
        copy_name = frappe.db.get_value("Library Copy", {"barcode": scan_value}, "name") or frappe.db.get_value(
            "Library Copy", {"accession_no": scan_value}, "name"
        ) or frappe.db.get_value("Library Copy", scan_value, "name")
    elif item:
        copy_name = get_available_copy_for_item(item)
    else:
        frappe.throw("Enter a barcode/accession/copy or select an item.")

    if not copy_name:
        frappe.throw(f"No copy found for {scan_value or item}.")

    payload = _get_copy_payload(copy_name)
    payload["member"] = _get_member_payload(member)
    payload["copy_member"] = _get_member_payload(payload["copy"].get("current_member"))
    return payload


@frappe.whitelist()
def issue_library_copy(member: str, scan_value: str = "", item: str | None = None, reservation_name: str | None = None):
    if scan_value:
        transaction = issue_by_scan(member, scan_value, reservation_name=reservation_name)
    elif item:
        transaction = issue_by_item(member, item, reservation_name=reservation_name)
    else:
        frappe.throw("Enter a barcode/accession/copy or select an item.")
    return transaction.as_dict()


@frappe.whitelist()
def return_library_copy(scan_value: str, condition_status="Good", mark_lost=0, notes=None):
    transaction = return_copy(scan_value, condition_status=condition_status, mark_lost=int(mark_lost), notes=notes)
    return transaction.as_dict()


@frappe.whitelist()
def renew_library_transaction(transaction: str):
    doc = renew_transaction(transaction)
    return doc.as_dict()


@frappe.whitelist()
def reserve_library_item(member: str, item: str, copy: str | None = None, notes: str | None = None):
    reservation = place_reservation(member, item, copy=copy, notes=notes)
    return reservation.as_dict()
