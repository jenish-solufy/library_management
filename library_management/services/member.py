from __future__ import annotations

import frappe
from frappe.utils import cint, getdate, today


BLOCKED_STATUSES = {"Suspended", "Blacklisted", "Inactive"}


def validate_member_for_issue(member_name: str):
    member = frappe.get_doc("Library Member", member_name)
    if member.status in BLOCKED_STATUSES:
        frappe.throw(f"Member {member.name} is {member.status} and cannot borrow.")
    if member.validity_end_date and getdate(member.validity_end_date) < getdate(today()):
        frappe.throw(f"Membership for {member.name} has expired.")
    if cint(member.unpaid_fine_threshold) and member.outstanding_fines > cint(member.unpaid_fine_threshold):
        frappe.throw(f"Outstanding fines exceed the configured threshold for {member.name}.")
    return member


def refresh_member_counters(member_name: str):
    issued = frappe.db.count("Library Transaction", {"member": member_name, "status": ["in", ["Issued", "Overdue"]]})
    outstanding = (
        frappe.db.sql(
            """
            select coalesce(sum(outstanding_amount), 0)
            from `tabLibrary Fine`
            where member = %s and status in ('Unpaid', 'Partly Paid')
            """,
            member_name,
        )[0][0]
        or 0
    )
    frappe.db.set_value(
        "Library Member",
        member_name,
        {"current_issued_count": issued, "outstanding_fines": outstanding},
        update_modified=False,
    )


def expire_memberships():
    today_date = getdate(today())
    names = frappe.get_all(
        "Library Member",
        filters={"status": ["not in", ["Expired", "Blacklisted"]], "validity_end_date": ["<", today_date]},
        pluck="name",
    )
    for name in names:
        frappe.db.set_value("Library Member", name, "status", "Expired", update_modified=False)
        refresh_member_counters(name)
