from __future__ import annotations

import frappe
from frappe.utils import nowdate, add_days


from library_management.services.circulation import (
	get_available_copy_for_item,
	issue_by_item,
	issue_by_scan,
	renew_transaction,
	return_copy,
)
from library_management.services.reservation import place_reservation
from library_management.utils import get_item_availability


def _get_copy_payload(copy_name: str):
	copy = frappe.db.get_value(
		"Library Copy",
		copy_name,
		["name", "item", "accession_no", "barcode", "status", "current_member", "condition_status"],
		as_dict=True,
	)
	item = frappe.db.get_value(
		"Item",
		copy.item,
		["name", "item_name", "library_authors", "library_material_type", "library_front_cover", "library_back_cover"],
		as_dict=True,
	)
	return {"copy": copy, "item": item, "availability": get_item_availability(copy.item)}


def _get_member_payload(member_name: str | None):
	if not member_name:
		return None
	return frappe.db.get_value(
		"Library Member",
		member_name,
		["name", "member_name", "member_category", "status", "current_issued_count", "outstanding_fines"],
		as_dict=True,
	)


@frappe.whitelist()
def get_library_member_context(member: str):
	member_payload = _get_member_payload(member)
	if not member_payload:
		frappe.throw("Library Member not found.")
	return {"member": member_payload}


# @frappe.whitelist()
# def barcode_lookup(scan_value: str = "", item: str | None = None, member: str | None = None):
#     copy_name = None
#     if scan_value:
#         copy_name = frappe.db.get_value("Library Copy", {"barcode": scan_value}, "name") or frappe.db.get_value(
#             "Library Copy", {"accession_no": scan_value}, "name"
#         ) or frappe.db.get_value("Library Copy", scan_value, "name")
#     elif item:
#         copy_name = get_available_copy_for_item(item)
#     else:
#         frappe.throw("Enter a barcode/accession/copy or select an item.")

#     if not copy_name:
#         frappe.throw(f"No copy found for {scan_value or item}.")

#     payload = _get_copy_payload(copy_name)
#     payload["member"] = _get_member_payload(member)
#     payload["copy_member"] = _get_member_payload(payload["copy"].get("current_member"))
#     return payload


@frappe.whitelist()
def issue_library_copy(member: str, scan_value: str = "", item: str | None = None, reservation_name: str | None = None):
	if scan_value:
		transaction = issue_by_scan(member, scan_value, reservation_name=reservation_name)
	elif item:
		transaction = issue_by_item(member, item, reservation_name=reservation_name)
	else:
		frappe.throw("Enter a barcode/accession/copy or select an item.")
	return transaction.as_dict()


# @frappe.whitelist()
# def return_library_copy(scan_value: str, condition_status="Good", mark_lost=0, notes=None):
#     transaction = return_copy(scan_value, condition_status=condition_status, mark_lost=int(mark_lost), notes=notes)
#     return transaction.as_dict()

@frappe.whitelist()
def return_library_copy(scan_value=None, condition_status=None, notes=None):
	if not scan_value:
		frappe.throw("Scan value is required")

	copy_name = (
		frappe.db.get_value("Library Copy", {"name": scan_value}, "name")
		or frappe.db.get_value("Library Copy", {"barcode": scan_value}, "name")
		or frappe.db.get_value("Library Copy", {"accession_no": scan_value}, "name")
	)

	if not copy_name:
		frappe.throw("Library Copy not found")

	active_txn = get_active_issue_transaction(copy_name)
	# frappe.throw(f'{active_txn}')
	if not active_txn:
		frappe.throw("No active issue transaction found for this copy")

	return_doc = frappe.new_doc("Library Transaction")
	return_doc.transaction_type = "Return"
	return_doc.member = active_txn.member
	return_doc.copy = copy_name
	return_doc.item = active_txn.item
	return_doc.issue_date = active_txn.issue_date
	return_doc.due_date = active_txn.due_date
	
	return_doc.from_date = nowdate()
	return_doc.notes = notes or ""
	return_doc.status = "Returned"

	if hasattr(return_doc, "condition_status"):
		return_doc.condition_status = condition_status or "Good"

	return_doc.insert(ignore_permissions=True)
	return_doc.submit()

	frappe.db.set_value("Library Copy", copy_name, {
		"status": "Available",
		"current_member": ""
	})

	frappe.db.commit()

	return {
		"name": return_doc.name,
		"status": return_doc.status
	}

@frappe.whitelist()
def renew_library_transaction(transaction=None, scan_value=None):
	if not transaction and not scan_value:
		frappe.throw("Transaction or Scan Value is required")

	# 🔹 If transaction is not given → find from scan_value
	if not transaction and scan_value:
		copy_name = (
			frappe.db.get_value("Library Copy", {"name": scan_value}, "name")
			or frappe.db.get_value("Library Copy", {"barcode": scan_value}, "name")
			or frappe.db.get_value("Library Copy", {"accession_no": scan_value}, "name")
		)

		if not copy_name:
			frappe.throw("Library Copy not found")

		active_txn = get_active_issue_transaction(copy_name)
		if not active_txn:
			frappe.throw("No active issued transaction found")

		transaction = active_txn.name

	# 🔹 Call your helper
	doc = renew_transaction(transaction)

	return {
		"name": doc.name,
		"status": doc.status,
		"due_date": doc.due_date,
		"renewal_count": doc.renewal_count
	}

# def renew_library_transaction(transaction: str):
#     doc = renew_transaction(transaction)
#     return doc.as_dict()


@frappe.whitelist()
def reserve_library_item(member: str, item: str, copy: str | None = None, notes: str | None = None):
	reservation = place_reservation(member, item, copy=copy, notes=notes)
	return reservation.as_dict()

import frappe
from frappe.utils import nowdate, add_days

def get_active_issue_transaction(copy_name):
	
	txn_name = frappe.db.get_value(
		"Library Transaction",
		{
			"copy": copy_name,
			
			"transaction_type": ["in", ["Issue", "Renew"]],
			"status": ["in", ["Issued", "Overdue", "Renewed"]],
		},
		"name",
		order_by="creation desc"
	)
	if not txn_name:
		return None

	return frappe.get_doc("Library Transaction", txn_name)



@frappe.whitelist()
def barcode_lookup(scan_value=None, item=None, member=None):
	result = {
		"copy": None,
		"item": None,
		"member": None,
		"copy_member": None,
		"active_transaction": None,
		"next_action": None,
		"availability": {
			"total_copies": 0,
			"available_copies": 0,
			"issued_copies": 0,
			"reserved_copies": 0
		}
	}

	copy_name = None

	if scan_value:
		copy_name = (
			frappe.db.get_value("Library Copy", {"name": scan_value}, "name")
			or frappe.db.get_value("Library Copy", {"barcode": scan_value}, "name")
			or frappe.db.get_value("Library Copy", {"accession_no": scan_value}, "name")
		)

	if copy_name:
		copy_doc = frappe.get_doc("Library Copy", copy_name)

		result["copy"] = {
			"name": copy_doc.name,
			"item": copy_doc.item,
			"barcode": getattr(copy_doc, "barcode", None),
			"accession_no": getattr(copy_doc, "accession_no", None),
			"status": getattr(copy_doc, "status", None),
			"current_member": getattr(copy_doc, "current_member", None),
		}

		if copy_doc.item:
			item_doc = frappe.get_doc("Item", copy_doc.item)
			result["item"] = {
				"name": item_doc.name,
				"item_name": item_doc.item_name,
				"library_authors": getattr(item_doc, "library_authors", None),
				"library_material_type": getattr(item_doc, "library_material_type", None),
				"library_front_cover": getattr(item_doc, "library_front_cover", None),
				"library_back_cover": getattr(item_doc, "library_back_cover", None),
			}

			total_copies = frappe.db.count("Library Copy", {"item": copy_doc.item})
			available_copies = frappe.db.count("Library Copy", {"item": copy_doc.item, "status": "Available"})
			issued_copies = frappe.db.count(
				"Library Copy",
				{"item": copy_doc.item, "status": ["in", ["Issued", "Overdue", "Renewed"]]}
			)

			result["availability"] = {
				"total_copies": total_copies,
				"available_copies": available_copies,
				"issued_copies": issued_copies,
				"reserved_copies": 0
			}

		active_txn = get_active_issue_transaction(copy_doc.name)
		# frappe.throw(f'{active_txn}')
		if active_txn:
			result["active_transaction"] = {
				"name": active_txn.name,
				"transaction_type": active_txn.transaction_type,
				"status": active_txn.status,
				"member": active_txn.member,
				"due_date": getattr(active_txn, "to_date", None),
			}
			result["next_action"] = "return"

			if active_txn.member:
				member_doc = frappe.get_doc("Library Member", active_txn.member)
				result["copy_member"] = {
					"name": member_doc.name,
					"member_name": member_doc.member_name,
					"member_category": getattr(member_doc, "member_category", None),
					"status": getattr(member_doc, "status", None),
					"current_issued_count": getattr(member_doc, "current_issued_count", 0),
					"outstanding_fines": getattr(member_doc, "outstanding_fines", 0),
				}
		else:
			if copy_doc.status == "Available":
				result["next_action"] = "issue"

	elif item:
		item_doc = frappe.get_doc("Item", item)
		result["item"] = {
			"name": item_doc.name,
			"item_name": item_doc.item_name,
			"library_authors": getattr(item_doc, "library_authors", None),
			"library_material_type": getattr(item_doc, "library_material_type", None),
			"library_front_cover": getattr(item_doc, "library_front_cover", None),
			"library_back_cover": getattr(item_doc, "library_back_cover", None),
		}

		total_copies = frappe.db.count("Library Copy", {"item": item})
		available_copies = frappe.db.count("Library Copy", {"item": item, "status": "Available"})
		issued_copies = frappe.db.count(
			"Library Copy",
			{"item": item, "status": ["in", ["Issued", "Overdue", "Renewed"]]}
		)

		result["availability"] = {
			"total_copies": total_copies,
			"available_copies": available_copies,
			"issued_copies": issued_copies,
			"reserved_copies": 0
		}

		if available_copies > 0:
			result["next_action"] = "issue"
		else:
			result["next_action"] = "return"

	if member:
		member_doc = frappe.get_doc("Library Member", member)
		result["member"] = {
			"name": member_doc.name,
			"member_name": member_doc.member_name,
			"member_category": getattr(member_doc, "member_category", None),
			"status": getattr(member_doc, "status", None),
			"current_issued_count": getattr(member_doc, "current_issued_count", 0),
			"outstanding_fines": getattr(member_doc, "outstanding_fines", 0),
		}

	return result





