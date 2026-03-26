frappe.ui.form.on("Library Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Create School Demo Data"), () => {
			frappe.call("library_management.setup.demo.create_school_demo_data");
		});
		frm.add_custom_button(__("Create Public Demo Data"), () => {
			frappe.call("library_management.setup.demo.create_public_library_demo_data");
		});
	}
});
