import frappe


def execute(filters=None):
    columns = [
        {"label": "Member", "fieldname": "name", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Member Name", "fieldname": "member_name", "fieldtype": "Data", "width": 180},
        {"label": "Category", "fieldname": "member_category", "fieldtype": "Data", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Valid Till", "fieldname": "validity_end_date", "fieldtype": "Date", "width": 100},
    ]
    data = frappe.get_all(
        "Library Member",
        fields=["name", "member_name", "member_category", "status", "validity_end_date"],
        order_by="validity_end_date asc",
    )
    return columns, data
