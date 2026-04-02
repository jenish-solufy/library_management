import frappe
from frappe.model.document import Document

from library_management.utils import DEFAULT_MEMBER_POLICIES


class LibrarySettings(Document):
    def validate(self):
        self.use_item_as_catalog_master = 1
        self.ensure_policy_defaults()
        self.ensure_fine_defaults()

    def ensure_policy_defaults(self):
        existing = {row.member_category for row in self.member_policies}
        for category, defaults in DEFAULT_MEMBER_POLICIES.items():
            if category in existing:
                continue
            self.append("member_policies", {"member_category": category, **defaults})

    def ensure_fine_defaults(self):
        existing = {row.member_category for row in self.fine_rules}
        for category in DEFAULT_MEMBER_POLICIES:
            if category in existing:
                continue
            self.append(
                "fine_rules",
                {
                    "member_category": category,
                    "grace_period_days": 0,
                    "daily_fine": 5 if category == "Student" else 10,
                    "max_fine_amount": 500,
                    "lost_item_multiplier": 1.0,
                    "damaged_item_flat_fee": 100,
                    "processing_fee": 0,
                    "fine_waiver_limit": 250,
                },
            )
