from frappe.model.document import Document
from frappe.model.naming import make_autoname


class LibraryFine(Document):
    def autoname(self):
        if not self.name or self.name.startswith("New Library Fine"):
            self.name = make_autoname("LIB-FINE-.YYYY.-.#####")

    def validate(self):
        self.outstanding_amount = max((self.amount or 0) - (self.paid_amount or 0) - (self.waived_amount or 0), 0)
        if self.outstanding_amount <= 0:
            self.status = "Paid" if (self.paid_amount or 0) >= (self.amount or 0) else "Waived"
        elif self.paid_amount:
            self.status = "Partly Paid"
        else:
            self.status = "Unpaid"
