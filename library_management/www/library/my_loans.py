import frappe


def get_context(context):
    member = frappe.db.get_value("Library Member", {"user": frappe.session.user}, "name")
    context.title = "My Library Loans"
    context.loans = []
    if member:
        context.loans = frappe.get_all(
            "Library Transaction",
            filters={"member": member},
            fields=["name", "item", "copy", "issue_date", "due_date", "return_date", "status"],
            order_by="modified desc",
        )
    return context
