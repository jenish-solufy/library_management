from __future__ import annotations

import frappe
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt, getdate

from library_management.utils import get_library_settings


def _make_accession_no(prefix: str) -> str:
    series_prefix = (prefix or "ACC-").replace('"', "").strip()
    if not series_prefix.endswith("-"):
        series_prefix = f"{series_prefix}-"
    return make_autoname(f"{series_prefix}.YYYY.-.#####")


def _make_barcode(prefix: str) -> str:
    series_prefix = (prefix or "LIB-BC-").replace('"', "").strip()
    if not series_prefix.endswith("-"):
        series_prefix = f"{series_prefix}-"
    return make_autoname(f"{series_prefix}.YYYY.-.#####")


def on_purchase_receipt_submit(doc, method=None):
    settings = get_library_settings()
    if not cint(settings.enable_auto_copy_creation_from_purchase):
        return

    configured_group = (settings.auto_copy_creation_item_group or "").strip()
    accession_prefix = settings.accession_series_prefix or "ACC-"
    barcode_prefix = settings.barcode_series_prefix or "LIB-BC-"

    for row in doc.items:
        item_code = row.item_code
        if not item_code:
            continue

        if not cint(frappe.db.get_value("Item", item_code, "library_is_catalog_item") or 0):
            continue

        if configured_group:
            item_group = frappe.db.get_value("Item", item_code, "item_group")
            if item_group != configured_group:
                continue

        qty = cint(row.qty or 0)
        if qty <= 0:
            continue

        source_key = f"Purchase Receipt:{doc.name}:{row.name}"
        existing = cint(
            frappe.db.count(
                "Library Copy",
                {
                    "item": item_code,
                    "acquisition_source": source_key,
                },
            )
        )

        to_create = max(qty - existing, 0)
        for _ in range(to_create):
            copy = frappe.get_doc(
                {
                    "doctype": "Library Copy",
                    "item": item_code,
                    "accession_no": _make_accession_no(accession_prefix),
                    "barcode": _make_barcode(barcode_prefix),
                    "status": "Available",
                    "acquisition_date": getdate(doc.posting_date),
                    "acquisition_source": source_key,
                    "purchase_price": flt(row.valuation_rate or row.rate or 0),
                }
            )
            copy.insert(ignore_permissions=True)

