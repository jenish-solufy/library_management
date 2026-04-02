frappe.ui.form.on("Library Transaction", {
	refresh(frm) {
		if (frm.doc.status === "Issued" || frm.doc.status === "Overdue") {
			frm.add_custom_button(__("Renew"), () => {
				frappe.call("library_management.api.renew_library_transaction", { transaction: frm.doc.name }).then(() => frm.reload_doc());
			});
		}
	}
});
