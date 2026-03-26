import frappe


def execute(filters=None):
    columns = [
        {"label": "Shelf", "fieldname": "shelf", "fieldtype": "Link", "options": "Library Shelf", "width": 150},
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Accession No", "fieldname": "accession_no", "fieldtype": "Data", "width": 140},
        {"label": "Barcode", "fieldname": "barcode", "fieldtype": "Data", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.get_all(
        "Library Copy",
        fields=["shelf", "item", "accession_no", "barcode", "status"],
        order_by="shelf asc, item asc",
    )
    return columns, data
