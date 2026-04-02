import frappe
from frappe.utils import today


def execute(filters=None):
    filters = filters or {}
    posting_date = filters.get("date") or today()
    columns = [
        {"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Library Transaction", "width": 150},
        {"label": "Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 100},
        {"label": "Member", "fieldname": "member", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Copy", "fieldname": "copy", "fieldtype": "Link", "options": "Library Copy", "width": 150},
        {"label": "Issue Date", "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
        {"label": "Return Date", "fieldname": "return_date", "fieldtype": "Date", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql(
        """
        select name, transaction_type, member, item, copy, issue_date, return_date, status
        from `tabLibrary Transaction`
        where issue_date = %(date)s or return_date = %(date)s
        order by modified desc
        """,
        {"date": posting_date},
        as_dict=True,
    )
    return columns, data
