import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import add_days, getdate, today

from library_management.services.member import refresh_member_counters
from library_management.utils import get_library_settings


class LibraryMember(Document):
    def autoname(self):
        if not self.name or self.name.startswith("New Library Member"):
            self.name = make_autoname("LIB-MEM-.YYYY.-.#####")

    def validate(self):
        self.sync_plan_defaults()
        self.sync_linked_identity()
        self.update_status_from_validity()

    def on_update(self):
        refresh_member_counters(self.name)

    def sync_plan_defaults(self):
        if not self.membership_plan:
            return
        plan = frappe.get_doc("Library Membership Plan", self.membership_plan)
        if not self.member_category:
            self.member_category = plan.default_member_category
        if not self.validity_start_date:
            self.validity_start_date = today()
        if not self.validity_end_date and plan.validity_days:
            self.validity_end_date = add_days(self.validity_start_date, plan.validity_days)
        if not self.deposit_amount:
            self.deposit_amount = plan.deposit_amount

    def sync_linked_identity(self):
        if self.student and not self.user:
            self.user = frappe.db.get_value("Student", self.student, "student_email_id")
        if self.employee and not self.user:
            self.user = frappe.db.get_value("Employee", self.employee, "user_id")
        if self.user and not self.email:
            self.email = frappe.db.get_value("User", self.user, "email")

    def update_status_from_validity(self):
        settings = get_library_settings()
        if not self.validity_start_date:
            self.validity_start_date = today()
        if not self.validity_end_date:
            self.validity_end_date = add_days(self.validity_start_date, settings.default_membership_validity_days or 365)
        if self.status not in {"Blacklisted", "Suspended", "Inactive"} and self.validity_end_date and getdate(self.validity_end_date) < getdate(today()):
            self.status = "Expired"
