import frappe


def execute(filters=None):
    columns = [
        {"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Library Transaction", "width": 150},
        {"label": "Member", "fieldname": "member", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Copy", "fieldname": "copy", "fieldtype": "Link", "options": "Library Copy", "width": 150},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Overdue Days", "fieldname": "overdue_days", "fieldtype": "Int", "width": 100},
    ]
    data = frappe.get_all(
        "Library Transaction",
        filters={"status": "Overdue"},
        fields=["name", "member", "item", "copy", "due_date", "overdue_days"],
        order_by="due_date asc",
    )
    return columns, data
