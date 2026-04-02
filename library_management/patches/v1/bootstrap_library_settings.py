import frappe


def execute():
    if not frappe.db.exists("DocType", "Library Settings"):
        return
    settings = frappe.get_single("Library Settings")
    if not settings.library_name:
        settings.library_name = "Library Management"
    settings.save(ignore_permissions=True)
