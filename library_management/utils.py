from __future__ import annotations

from datetime import timedelta

import frappe
from frappe.utils import add_days, cint, getdate, today


DEFAULT_MEMBER_POLICIES = {
    "Student": {"max_books": 2, "loan_period_days": 14, "max_renewals": 1, "grace_period_days": 1},
    "Teacher": {"max_books": 10, "loan_period_days": 30, "max_renewals": 3, "grace_period_days": 2},
    "Staff": {"max_books": 5, "loan_period_days": 21, "max_renewals": 2, "grace_period_days": 2},
    "Public Member": {"max_books": 4, "loan_period_days": 14, "max_renewals": 1, "grace_period_days": 1},
    "Guest": {"max_books": 1, "loan_period_days": 7, "max_renewals": 0, "grace_period_days": 0},
}


def get_library_settings():
    return frappe.get_cached_doc("Library Settings")


def get_member_policy(category: str) -> frappe._dict:
    settings = get_library_settings()
    for row in settings.member_policies:
        if row.member_category == category:
            return frappe._dict(row.as_dict())

    defaults = DEFAULT_MEMBER_POLICIES.get(category, DEFAULT_MEMBER_POLICIES["Public Member"])
    return frappe._dict(defaults | {"member_category": category})


def get_fine_rule(category: str) -> frappe._dict:
    settings = get_library_settings()
    for row in settings.fine_rules:
        if row.member_category == category:
            return frappe._dict(row.as_dict())

    return frappe._dict(
        {
            "member_category": category,
            "grace_period_days": 0,
            "daily_fine": 0,
            "max_fine_amount": 0,
            "lost_item_multiplier": 1,
            "damaged_item_flat_fee": 0,
            "processing_fee": 0,
            "fine_waiver_limit": 0,
        }
    )


def get_due_date(issue_date, member_category: str, item=None):
    item_loan_period = None
    if item:
        item_loan_period = cint(frappe.db.get_value("Item", item, "library_default_loan_period"))

    policy = get_member_policy(member_category)
    loan_days = item_loan_period or cint(policy.loan_period_days) or 14
    return add_days(issue_date or today(), loan_days)


def calculate_days_overdue(due_date, return_date=None, grace_days: int = 0) -> int:
    if not due_date:
        return 0
    effective_date = getdate(return_date or today())
    overdue = (effective_date - getdate(due_date)).days - cint(grace_days)
    return max(overdue, 0)


def coalesce(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None


def get_item_availability(item: str) -> frappe._dict:
    result = frappe.db.sql(
        """
        select
            count(name) as total_copies,
            sum(case when status = 'Available' then 1 else 0 end) as available_copies,
            sum(case when status = 'Issued' then 1 else 0 end) as issued_copies,
            sum(case when status = 'Reserved' then 1 else 0 end) as reserved_copies
        from `tabLibrary Copy`
        where item = %s
        """,
        item,
        as_dict=True,
    )[0]
    return frappe._dict(result)


def daterange_days(start_date, end_date):
    current = getdate(start_date)
    end = getdate(end_date)
    while current <= end:
        yield current
        current += timedelta(days=1)
