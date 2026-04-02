frappe.ui.form.on("Library Member", {
	refresh(frm) {
		render_previous_allocations(frm);
		if (!frm.is_new()) {
			frm.add_custom_button(__("Reserve Title"), () => {
				frappe.new_doc("Library Reservation", { member: frm.doc.name });
			});
			frm.add_custom_button(__("Issue Item"), () => {
				frappe.new_doc("Library Transaction", { member: frm.doc.name });
			});
		}
	}
});

function render_previous_allocations(frm) {
	const wrapper = frm.fields_dict.previous_allocation_html?.$wrapper;
	if (!wrapper) return;

	if (frm.is_new()) {
		wrapper.html(`<div class="text-muted small">${__("Save the member to view allocation history.")}</div>`);
		return;
	}

	frappe.db
		.get_list("Library Transaction", {
			filters: { member: frm.doc.name },
			fields: ["name", "transaction_type", "status", "item", "copy", "issue_date", "return_date"],
			order_by: "modified desc",
			limit: 5
		})
		.then((rows) => {
			const row_html = (rows || [])
				.map(
					(row) => `
						<tr>
							<td><a href="/app/library-transaction/${encodeURIComponent(row.name)}">${frappe.utils.escape_html(row.name)}</a></td>
							<td>${frappe.utils.escape_html(row.transaction_type || "-")}</td>
							<td>${frappe.utils.escape_html(row.status || "-")}</td>
							<td>${frappe.utils.escape_html(row.item || "-")}</td>
							<td>${frappe.utils.escape_html(row.copy || "-")}</td>
							<td>${frappe.datetime.str_to_user(row.issue_date || "") || "-"}</td>
							<td>${frappe.datetime.str_to_user(row.return_date || "") || "-"}</td>
						</tr>
					`
				)
				.join("");

			const content = `
				<div class="small text-muted" style="margin-bottom: 8px;">
					${__("Showing last 5 allocations for this member.")}
				</div>
				<div class="table-responsive">
					<table class="table table-bordered table-condensed">
						<thead>
							<tr>
								<th>${__("Transaction")}</th>
								<th>${__("Type")}</th>
								<th>${__("Status")}</th>
								<th>${__("Item")}</th>
								<th>${__("Copy")}</th>
								<th>${__("Issue Date")}</th>
								<th>${__("Return Date")}</th>
							</tr>
						</thead>
						<tbody>
							${row_html || `<tr><td colspan="7" class="text-muted">${__("No allocation history found.")}</td></tr>`}
						</tbody>
					</table>
				</div>
				<div style="margin-top: 8px;">
					<button class="btn btn-xs btn-default" data-action="see-more-alloc">${__("See More")}</button>
				</div>
			`;

			wrapper.html(content);
			wrapper.find("[data-action='see-more-alloc']").on("click", () => {
				frappe.set_route("List", "Library Transaction", { member: frm.doc.name });
			});
		});
}
