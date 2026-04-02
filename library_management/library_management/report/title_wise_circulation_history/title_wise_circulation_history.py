import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Library Transaction", "width": 150},
        {"label": "Member", "fieldname": "member", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Issue Date", "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
        {"label": "Return Date", "fieldname": "return_date", "fieldtype": "Date", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.get_all(
        "Library Transaction",
        filters={"item": filters.get("item")} if filters.get("item") else {},
        fields=["item", "name", "member", "issue_date", "return_date", "status"],
        order_by="issue_date desc",
    )
    return columns, data
