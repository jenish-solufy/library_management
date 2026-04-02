import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class LibraryTransaction(Document):
    def autoname(self):
        if not self.name or self.name.startswith("New Library Transaction"):
            self.name = make_autoname("LIB-TXN-.YYYY.-.#####")

    def validate(self):
        if self.member and not self.member_category:
            self.member_category = frappe.db.get_value("Library Member", self.member, "member_category")
        if self.copy:
            if not self.item:
                self.item = frappe.db.get_value("Library Copy", self.copy, "item")
            if not self.valuation_rate:
                self.valuation_rate = frappe.db.get_value("Library Copy", self.copy, "purchase_price") or 0
        if self.issue_date and self.due_date and self.due_date < self.issue_date:
            frappe.throw("Due date cannot be earlier than issue date.")
        if self.return_date and self.issue_date and self.return_date < self.issue_date:
            frappe.throw("Return date cannot be earlier than issue date.")
