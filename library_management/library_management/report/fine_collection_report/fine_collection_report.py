import frappe


def execute(filters=None):
    columns = [
        {"label": "Fine", "fieldname": "name", "fieldtype": "Link", "options": "Library Fine", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Member", "fieldname": "member", "fieldtype": "Link", "options": "Library Member", "width": 150},
        {"label": "Charge Type", "fieldname": "charge_type", "fieldtype": "Data", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": "Paid", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Outstanding", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.get_all(
        "Library Fine",
        fields=["name", "posting_date", "member", "charge_type", "amount", "paid_amount", "outstanding_amount", "status"],
        order_by="posting_date desc",
    )
    return columns, data
