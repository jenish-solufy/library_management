import frappe


def execute(filters=None):
    columns = [
        {"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Library Transaction", "width": 150},
        {"label": "Member", "fieldname": "member", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Copy", "fieldname": "copy", "fieldtype": "Link", "options": "Library Copy", "width": 150},
        {"label": "Issue Date", "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.get_all(
        "Library Transaction",
        filters={"status": ["in", ["Issued", "Overdue"]]},
        fields=["name", "member", "item", "copy", "issue_date", "due_date", "status"],
        order_by="due_date asc",
    )
    return columns, data
