import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


ITEM_CUSTOM_FIELDS = {
    "Item": [
        {"fieldname": "library_section", "fieldtype": "Section Break", "label": "Library Management", "insert_after": "has_serial_no"},
        {"fieldname": "library_is_catalog_item", "fieldtype": "Check", "label": "Library Catalog Item", "default": "1", "insert_after": "library_section"},
        {
            "fieldname": "library_material_type",
            "fieldtype": "Select",
            "label": "Library Material Type",
            "options": "\nBook\nJournal\nMagazine\nNewspaper\nThesis\nAudio\nVideo\nDVD\neBook\nReference Material\nManuscript\nArchive",
            "insert_after": "library_is_catalog_item",
            "in_list_view": 1,
        },
        {"fieldname": "library_is_reference_only", "fieldtype": "Check", "label": "Reference Only", "insert_after": "library_material_type"},
        {"fieldname": "library_is_borrowable", "fieldtype": "Check", "label": "Borrowable", "default": "1", "insert_after": "library_is_reference_only"},
        {"fieldname": "library_default_loan_period", "fieldtype": "Int", "label": "Default Loan Period (Days)", "insert_after": "library_is_borrowable"},
        {"fieldname": "library_isbn_10", "fieldtype": "Data", "label": "ISBN-10", "insert_after": "library_default_loan_period"},
        {"fieldname": "library_isbn_13", "fieldtype": "Data", "label": "ISBN-13", "insert_after": "library_isbn_10"},
        {"fieldname": "library_authors", "fieldtype": "Small Text", "label": "Authors", "insert_after": "library_isbn_13"},
        {"fieldname": "library_publisher", "fieldtype": "Data", "label": "Publisher", "insert_after": "library_authors"},
        {"fieldname": "library_edition", "fieldtype": "Data", "label": "Edition", "insert_after": "library_publisher"},
        {"fieldname": "library_language", "fieldtype": "Data", "label": "Language", "insert_after": "library_edition"},
        {"fieldname": "library_publication_year", "fieldtype": "Int", "label": "Publication Year", "insert_after": "library_language"},
        {"fieldname": "library_subject", "fieldtype": "Data", "label": "Subject / Genre", "insert_after": "library_publication_year"},
        {"fieldname": "library_classification_code", "fieldtype": "Data", "label": "Classification Code", "insert_after": "library_subject"},
        {"fieldname": "library_keywords", "fieldtype": "Small Text", "label": "Keywords", "insert_after": "library_classification_code"},
        {"fieldname": "library_summary", "fieldtype": "Small Text", "label": "Summary / Abstract", "insert_after": "library_keywords"},
        {"fieldname": "library_front_cover", "fieldtype": "Attach Image", "label": "Front Cover", "insert_after": "library_summary"},
        {"fieldname": "library_back_cover", "fieldtype": "Attach Image", "label": "Back Cover", "insert_after": "library_front_cover"},
    ],
    "Sales Invoice": [
        {"fieldname": "library_member", "fieldtype": "Link", "label": "Library Member", "options": "Library Member", "insert_after": "customer"},
        {"fieldname": "library_transaction", "fieldtype": "Link", "label": "Library Transaction", "options": "Library Transaction", "insert_after": "library_member"},
        {"fieldname": "library_fine", "fieldtype": "Link", "label": "Library Fine", "options": "Library Fine", "insert_after": "library_transaction"},
    ],
}


def after_install():
    create_custom_fields(ITEM_CUSTOM_FIELDS, update=True)
    ensure_roles()
    ensure_defaults()


def ensure_roles():
    for role_name in ("Library Manager", "Librarian", "Library Assistant", "Library Member"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert()


def ensure_defaults():
    if frappe.db.exists("Item Group", "Library Materials"):
        return

    parent = "All Item Groups"
    if not frappe.db.exists("Item Group", parent):
        return

    frappe.get_doc(
        {
            "doctype": "Item Group",
            "item_group_name": "Library Materials",
            "parent_item_group": parent,
            "is_group": 0,
        }
    ).insert(ignore_permissions=True)
