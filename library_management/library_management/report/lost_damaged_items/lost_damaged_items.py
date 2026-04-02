import frappe


def execute(filters=None):
    columns = [
        {"label": "Copy", "fieldname": "name", "fieldtype": "Link", "options": "Library Copy", "width": 150},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Condition", "fieldname": "condition_status", "fieldtype": "Data", "width": 120},
        {"label": "Current Member", "fieldname": "current_member", "fieldtype": "Link", "options": "Library Member", "width": 150},
    ]
    data = frappe.get_all(
        "Library Copy",
        filters={"status": ["in", ["Lost", "Damaged", "Under Repair", "Withdrawn"]]},
        fields=["name", "item", "status", "condition_status", "current_member"],
        order_by="modified desc",
    )
    return columns, data
