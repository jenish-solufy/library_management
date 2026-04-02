frappe.ui.form.on("Library Copy", {
	item(frm) {
		if (!frm.doc.accession_no && frm.doc.item) {
			frm.set_value("accession_no", "");
		}
	}
});
