import frappe


SELF_SERVICE_ROLES = {"Library Member"}
STAFF_ROLES = {"Library Manager", "Librarian", "Library Assistant", "System Manager"}


def _is_staff():
    return bool(STAFF_ROLES.intersection(set(frappe.get_roles())))


def _get_member_name_for_user(user=None):
    user = user or frappe.session.user
    if user == "Administrator":
        return None
    return frappe.db.get_value("Library Member", {"user": user}, "name")


def _self_query(fieldname="member"):
    member = _get_member_name_for_user()
    if not member:
        return "1=0"
    return f"`tab{{doctype}}`.`{fieldname}` = {frappe.db.escape(member)}"


def get_library_member_permission_query(user=None):
    if _is_staff():
        return ""
    member = _get_member_name_for_user(user)
    if not member:
        return "1=0"
    return f"`tabLibrary Member`.`name` = {frappe.db.escape(member)}"


def get_library_transaction_permission_query(user=None):
    if _is_staff():
        return ""
    member = _get_member_name_for_user(user)
    if not member:
        return "1=0"
    return f"`tabLibrary Transaction`.`member` = {frappe.db.escape(member)}"


def get_library_reservation_permission_query(user=None):
    if _is_staff():
        return ""
    member = _get_member_name_for_user(user)
    if not member:
        return "1=0"
    return f"`tabLibrary Reservation`.`member` = {frappe.db.escape(member)}"


def get_library_fine_permission_query(user=None):
    if _is_staff():
        return ""
    member = _get_member_name_for_user(user)
    if not member:
        return "1=0"
    return f"`tabLibrary Fine`.`member` = {frappe.db.escape(member)}"


def has_library_member_permission(doc, user=None, permission_type=None):
    return _is_staff() or doc.name == _get_member_name_for_user(user)


def has_library_transaction_permission(doc, user=None, permission_type=None):
    return _is_staff() or doc.member == _get_member_name_for_user(user)


def has_library_reservation_permission(doc, user=None, permission_type=None):
    return _is_staff() or doc.member == _get_member_name_for_user(user)


def has_library_fine_permission(doc, user=None, permission_type=None):
    return _is_staff() or doc.member == _get_member_name_for_user(user)
