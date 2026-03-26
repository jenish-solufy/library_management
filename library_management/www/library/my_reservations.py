import frappe


def get_context(context):
    member = frappe.db.get_value("Library Member", {"user": frappe.session.user}, "name")
    context.title = "My Library Reservations"
    context.reservations = []
    if member:
        context.reservations = frappe.get_all(
            "Library Reservation",
            filters={"member": member},
            fields=["name", "item", "copy", "status", "reservation_date", "expires_on", "queue_position"],
            order_by="modified desc",
        )
    return context
