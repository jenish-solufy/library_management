from __future__ import annotations

import frappe
from frappe.utils import flt, today

from library_management.utils import calculate_days_overdue, get_fine_rule, get_library_settings


def calculate_overdue_fine(member_category: str, due_date, return_date=None):
    rule = get_fine_rule(member_category)
    overdue_days = calculate_days_overdue(due_date, return_date, rule.grace_period_days)
    amount = overdue_days * flt(rule.daily_fine)
    if flt(rule.max_fine_amount):
        amount = min(amount, flt(rule.max_fine_amount))
    return overdue_days, flt(amount)


def create_or_update_fine(transaction, charge_type="Overdue", amount=0, description=None):
    if not flt(amount):
        return None

    fine = None
    if transaction.fine:
        fine = frappe.get_doc("Library Fine", transaction.fine)
        fine.amount = flt(amount)
        fine.outstanding_amount = flt(amount) - flt(fine.paid_amount)
        if description:
            fine.notes = description
        fine.save(ignore_permissions=True)
    else:
        fine = frappe.get_doc(
            {
                "doctype": "Library Fine",
                "member": transaction.member,
                "transaction": transaction.name,
                "item": transaction.item,
                "copy": transaction.copy,
                "charge_type": charge_type,
                "amount": flt(amount),
                "outstanding_amount": flt(amount),
                "posting_date": today(),
                "notes": description,
            }
        ).insert(ignore_permissions=True)
        transaction.db_set("fine", fine.name, update_modified=False)

    maybe_create_accounting_document(fine)
    return fine


def maybe_create_accounting_document(fine):
    settings = get_library_settings()
    if not settings.enable_fines or not settings.create_accounting_entries_for_fines:
        return
    if fine.sales_invoice:
        return
    if not settings.fine_item or not settings.company or not settings.cost_center:
        return

    member = frappe.get_doc("Library Member", fine.member)
    customer = member.customer
    if not customer:
        return

    invoice = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "company": settings.company,
            "customer": customer,
            "posting_date": fine.posting_date,
            "library_member": fine.member,
            "library_transaction": fine.transaction,
            "library_fine": fine.name,
            "items": [
                {
                    "item_code": settings.fine_item,
                    "qty": 1,
                    "rate": fine.amount,
                    "cost_center": settings.cost_center,
                }
            ],
        }
    )
    invoice.insert(ignore_permissions=True)
    fine.db_set("sales_invoice", invoice.name, update_modified=False)
