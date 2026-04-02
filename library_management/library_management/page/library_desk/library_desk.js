frappe.pages["library-desk"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Library Desk"),
		single_column: true
	});

	const state = {
		member: null,
		copyMember: null,
		copyPayload: null,
		autoRefreshTimer: null,
		syncingFields: false
	};

	const body = $(`
		<div class="library-desk-shell">
			<style>
				.library-desk-shell {
					padding: 16px 10px 28px;
					background:
						radial-gradient(circle at top left, rgba(233, 197, 106, 0.10), transparent 28%),
						radial-gradient(circle at top right, rgba(102, 140, 89, 0.10), transparent 26%);
				}
				.library-desk-layout {
					display: grid;
					grid-template-columns: minmax(0, 1.3fr) minmax(340px, 0.9fr);
					gap: 20px;
				}
				.library-panel {
					background: linear-gradient(180deg, #ffffff 0%, #fbfcf8 100%);
					border: 1px solid #d8e1cf;
					border-radius: 22px;
					box-shadow: 0 18px 36px rgba(30, 48, 18, 0.06);
					padding: 20px;
				}
				.library-panel--hero {
					background:
						linear-gradient(145deg, rgba(255, 248, 232, 0.96), rgba(248, 252, 243, 0.96)),
						#fff;
				}
				.library-kicker {
					font-size: 11px;
					font-weight: 700;
					text-transform: uppercase;
					letter-spacing: 0.14em;
					color: #76845f;
					margin-bottom: 8px;
				}
				.library-main-title {
					font-size: 30px;
					line-height: 1.05;
					font-weight: 700;
					color: #243319;
					margin: 0 0 10px;
				}
				.library-summary {
					color: #5c6950;
					max-width: 680px;
					margin-bottom: 10px;
				}
				.library-form-grid {
					display: grid;
					grid-template-columns: repeat(2, minmax(0, 1fr));
					gap: 14px;
				}
				.library-form-grid .full-span {
					grid-column: 1 / -1;
				}
				.library-control .form-group {
					margin-bottom: 0;
				}
				.library-chip-row {
					display: flex;
					flex-wrap: wrap;
					gap: 8px;
					margin-top: 16px;
				}
				.library-chip {
					background: #eef4e7;
					border: 1px solid #d8e5ca;
					border-radius: 999px;
					padding: 5px 10px;
					font-size: 12px;
					font-weight: 600;
					color: #476033;
				}
				.library-action-bar {
					display: flex;
					flex-wrap: wrap;
					gap: 10px;
					margin-top: 18px;
				}
				.library-feedback {
					margin-top: 16px;
				}
				.library-bottom-note {
					margin-top: 18px;
					padding-top: 14px;
					border-top: 1px solid #e2ead8;
				}
				.library-side-stack {
					display: grid;
					gap: 16px;
				}
				.library-side-title {
					font-size: 16px;
					font-weight: 700;
					color: #243319;
					margin: 0 0 12px;
				}
				.library-detail-grid {
					display: grid;
					grid-template-columns: 120px 1fr;
					row-gap: 9px;
					column-gap: 10px;
					font-size: 13px;
				}
				.library-detail-label {
					color: #6f7a67;
				}
				.library-detail-value {
					color: #223019;
					font-weight: 600;
				}
				.library-cover-grid {
					display: grid;
					grid-template-columns: repeat(2, minmax(0, 1fr));
					gap: 10px;
					margin-bottom: 12px;
				}
				.library-cover-card {
					background: #f8fbf3;
					border: 1px solid #d9e5ce;
					border-radius: 12px;
					padding: 8px;
				}
				.library-cover-label {
					font-size: 11px;
					color: #6f7a67;
					margin-bottom: 6px;
					text-transform: uppercase;
					letter-spacing: 0.05em;
				}
				.library-cover-img {
					width: 100%;
					height: 170px;
					object-fit: cover;
					border-radius: 8px;
					background: #e9efdf;
				}
				.library-cover-empty {
					height: 170px;
					border-radius: 8px;
					background: #edf3e3;
					border: 1px dashed #ccdab9;
					display: flex;
					align-items: center;
					justify-content: center;
					font-size: 12px;
					color: #6d7861;
				}
				.library-stat-grid {
					display: grid;
					grid-template-columns: repeat(3, minmax(0, 1fr));
					gap: 10px;
				}
				.library-stat {
					background: #f3f7ed;
					border: 1px solid #dfe8d5;
					border-radius: 16px;
					padding: 12px;
				}
				.library-stat-label {
					font-size: 11px;
					text-transform: uppercase;
					letter-spacing: 0.08em;
					color: #7a856d;
					margin-bottom: 4px;
				}
				.library-stat-value {
					font-size: 22px;
					line-height: 1;
					font-weight: 700;
					color: #23311a;
				}
				.library-muted {
					font-size: 12px;
					color: #6b7564;
					line-height: 1.5;
				}
				@media (max-width: 1024px) {
					.library-desk-layout,
					.library-form-grid,
					.library-stat-grid {
						grid-template-columns: 1fr;
					}
				}
			</style>
			<div class="library-desk-layout">
				<div class="library-panel library-panel--hero">
					<div class="library-kicker">${__("Circulation Desk")}</div>
					<h1 class="library-main-title">${__("Library Desk")}</h1>
					<div class="library-summary">${__("Scan a physical book first. The desk loads its state and shows only the next valid action.")}</div>

					<div class="library-form-grid">
						<div class="full-span library-control" data-control="scan_value"></div>
						<div class="full-span library-control" data-control="member"></div>
						<div class="full-span library-control" data-control="item"></div>
						<div class="library-control" data-control="condition_status"></div>
						<div class="library-control" data-control="notes"></div>
					</div>
					<div class="library-chip-row" data-role="chips"></div>

					<div class="library-action-bar">
						<button class="btn btn-primary hidden" data-action="issue">${__("Issue Copy")}</button>
						<button class="btn btn-secondary hidden" data-action="return">${__("Return Copy")}</button>
						<button class="btn btn-default hidden" data-action="reserve">${__("Reserve Title")}</button>
						<button class="btn btn-default" data-action="clear">${__("Clear")}</button>
					</div>

					<div class="library-feedback" data-role="feedback"></div>
					<div class="library-bottom-note">
						<div class="library-muted">${__("Scan works on a physical book copy. Use the optional title field only for title lookup or reservation when the book is not in hand.")}</div>
					</div>
				</div>

				<div class="library-side-stack">
					<div class="library-panel">
						<div class="library-side-title">${__("Member Snapshot")}</div>
						<div class="library-detail-grid">
							<div class="library-detail-label">${__("Member")}</div>
							<div class="library-detail-value" data-role="member_name">-</div>
							<div class="library-detail-label">${__("Category")}</div>
							<div class="library-detail-value" data-role="member_category">-</div>
							<div class="library-detail-label">${__("Status")}</div>
							<div class="library-detail-value" data-role="member_status">-</div>
							<div class="library-detail-label">${__("Issued Count")}</div>
							<div class="library-detail-value" data-role="member_issued_count">-</div>
							<div class="library-detail-label">${__("Outstanding Fines")}</div>
							<div class="library-detail-value" data-role="member_fines">-</div>
						</div>
					</div>

					<div class="library-panel">
						<div class="library-side-title">${__("Copy and Title Snapshot")}</div>
						<div data-role="cover_photos"></div>
						<div class="library-detail-grid">
							<div class="library-detail-label">${__("Copy")}</div>
							<div class="library-detail-value" data-role="copy_name">-</div>
							<div class="library-detail-label">${__("Title")}</div>
							<div class="library-detail-value" data-role="item_name">-</div>
							<div class="library-detail-label">${__("Authors")}</div>
							<div class="library-detail-value" data-role="authors">-</div>
							<div class="library-detail-label">${__("Material Type")}</div>
							<div class="library-detail-value" data-role="material_type">-</div>
							<div class="library-detail-label">${__("Status")}</div>
							<div class="library-detail-value" data-role="copy_status">-</div>
							<div class="library-detail-label">${__("Accession")}</div>
							<div class="library-detail-value" data-role="accession_no">-</div>
							<div class="library-detail-label">${__("Current Member")}</div>
							<div class="library-detail-value" data-role="current_member">-</div>
						</div>
					</div>

					<div class="library-panel">
						<div class="library-side-title">${__("Availability Overview")}</div>
						<div class="library-stat-grid">
							<div class="library-stat">
								<div class="library-stat-label">${__("Total Copies")}</div>
								<div class="library-stat-value" data-role="total_copies">0</div>
							</div>
							<div class="library-stat">
								<div class="library-stat-label">${__("Available")}</div>
								<div class="library-stat-value" data-role="available_copies">0</div>
							</div>
							<div class="library-stat">
								<div class="library-stat-label">${__("Issued")}</div>
								<div class="library-stat-value" data-role="issued_copies">0</div>
							</div>
						</div>
						<div class="library-muted" style="margin-top: 14px;">${__("Desk actions respond to the copy state shown here. If a title is not available, the reserve action becomes the preferred path.")}</div>
					</div>
				</div>
			</div>
		</div>
	`);

	$(page.body).append(body);

	const makeControl = (df, parent) => {
		const control = frappe.ui.form.make_control({ df, parent, render_input: true });
		control.refresh();
		return control;
	};

	const controls = {
		member: makeControl(
			{ fieldtype: "Link", label: __("Member"), fieldname: "member", options: "Library Member", reqd: 0, placeholder: __("Select member only when issuing or reserving") },
			body.find("[data-control='member']")
		),
		scan_value: makeControl(
			{ fieldtype: "Data", label: __("Book Barcode / Accession / Copy ID"), fieldname: "scan_value", placeholder: __("Scan the physical book barcode or accession no") },
			body.find("[data-control='scan_value']")
		),
		item: makeControl(
			{ fieldtype: "Link", label: __("Title (Optional)"), fieldname: "item", options: "Item", reqd: 0 },
			body.find("[data-control='item']")
		),
		condition_status: makeControl(
			{ fieldtype: "Select", label: __("Return Condition"), fieldname: "condition_status", options: "Good\nFair\nDamaged", default: "Good" },
			body.find("[data-control='condition_status']")
		),
		notes: makeControl(
			{ fieldtype: "Small Text", label: __("Notes"), fieldname: "notes" },
			body.find("[data-control='notes']")
		)
	};

	const getValue = (fieldname) => controls[fieldname].get_value();
	const setValue = (fieldname, value) => {
		state.syncingFields = true;
		controls[fieldname].set_value(value || "");
		window.setTimeout(() => {
			state.syncingFields = false;
		}, 0);
	};
	const setRoleValue = (role, value) => body.find(`[data-role='${role}']`).text(value ?? "-");
	const setActionVisible = (action, visible) => body.find(`[data-action='${action}']`).toggleClass("hidden", !visible);
	const lockMemberField = (locked) => controls.member.$input.prop("disabled", !!locked);

	const renderFeedback = (message = "", indicator = "blue") => {
		if (!message) {
			body.find("[data-role='feedback']").empty();
			return;
		}
		body.find("[data-role='feedback']").html(
			`<div class="alert alert-light border"><span class="indicator ${indicator}"></span> ${frappe.utils.escape_html(message)}</div>`
		);
	};

	const resetCopyAndAvailability = () => {
		body.find("[data-role='cover_photos']").empty();
		[
			"copy_name",
			"item_name",
			"authors",
			"material_type",
			"copy_status",
			"accession_no",
			"current_member"
		].forEach((field) => setRoleValue(field, "-"));
		["total_copies", "available_copies", "issued_copies"].forEach((field) => setRoleValue(field, 0));
	};

	const renderCoverPhotos = (item) => {
		const front = item?.library_front_cover;
		const back = item?.library_back_cover;

		const renderCard = (label, url) => {
			const content = url
				? `<img class="library-cover-img" src="${frappe.utils.escape_html(url)}" alt="${frappe.utils.escape_html(label)}">`
				: `<div class="library-cover-empty">${__("No Image")}</div>`;

			return `
				<div class="library-cover-card">
					<div class="library-cover-label">${frappe.utils.escape_html(label)}</div>
					${content}
				</div>
			`;
		};

		body.find("[data-role='cover_photos']").html(`
			<div class="library-cover-grid">
				${renderCard(__("Front Cover"), front)}
				${renderCard(__("Back Cover"), back)}
			</div>
		`);
	};

	const renderMember = (member) => {
		setRoleValue("member_name", member?.member_name || member?.name || "-");
		setRoleValue("member_category", member?.member_category || "-");
		setRoleValue("member_status", member?.status || "-");
		setRoleValue("member_issued_count", member?.current_issued_count ?? "-");
		setRoleValue("member_fines", member?.outstanding_fines ?? "-");
	};

	const renderCopyPayload = (payload) => {
		const availability = payload?.availability || {};
		const copy = payload?.copy || {};
		const item = payload?.item || {};

		setRoleValue("copy_name", copy.name || "-");
		setRoleValue("item_name", item.item_name || copy.item || "-");
		setRoleValue("authors", item.library_authors || "-");
		setRoleValue("material_type", item.library_material_type || "-");
		setRoleValue("copy_status", copy.status || "-");
		setRoleValue("accession_no", copy.accession_no || "-");
		setRoleValue("current_member", copy.current_member || "-");
		setRoleValue("total_copies", availability.total_copies || 0);
		setRoleValue("available_copies", availability.available_copies || 0);
		setRoleValue("issued_copies", availability.issued_copies || 0);
		renderCoverPhotos(item);
		if (copy.item) {
			setValue("item", copy.item);
		}
		if (copy.barcode || copy.accession_no || copy.name) {
			setValue("scan_value", copy.barcode || copy.accession_no || copy.name);
		}
	};

	const renderChips = () => {
		const chips = [];
		if (state.member?.status) chips.push(`Member: ${state.member.status}`);
		if (state.copyPayload?.copy?.status) chips.push(`Copy: ${state.copyPayload.copy.status}`);
		if (state.copyPayload?.availability?.reserved_copies) chips.push(`${state.copyPayload.availability.reserved_copies} reserved`);
		body.find("[data-role='chips']").html(
			chips.map((chip) => `<span class="library-chip">${frappe.utils.escape_html(chip)}</span>`).join("")
		);
	};

	const syncMemberStateFromCopy = () => {
		const scanValue = getValue("scan_value");
		const copyStatus = state.copyPayload?.copy?.status;
		const currentMember = state.copyPayload?.copy?.current_member;

		if (scanValue && ["Issued", "Overdue"].includes(copyStatus) && currentMember) {
			if (getValue("member") !== currentMember) {
				setValue("member", currentMember);
			}
			state.member = state.copyMember || state.member;
			lockMemberField(true);
			return;
		}

		if (scanValue && copyStatus === "Available") {
			lockMemberField(false);
			return;
		}

		lockMemberField(false);
	};

	const renderActions = () => {
		const hasScan = !!getValue("scan_value");
		const memberName = getValue("member") || state.member?.name;
		const hasMember = !!memberName;
		const hasItem = !!(getValue("item") || state.copyPayload?.item?.name);
		const copyStatus = state.copyPayload?.copy?.status;

		setActionVisible("issue", hasMember && (copyStatus === "Available" || (!hasScan && !copyStatus && hasItem)));
		setActionVisible("return", ["Issued", "Overdue"].includes(copyStatus));
		setActionVisible("reserve", hasMember && hasItem && ((!hasScan && !copyStatus) || ["Lost", "Damaged", "Withdrawn", "Under Repair", "Reference Only", "Reserved"].includes(copyStatus)));
	};

	const applyState = () => {
		syncMemberStateFromCopy();
		renderMember(state.member);
		if (state.copyPayload) {
			renderCopyPayload(state.copyPayload);
		} else {
			resetCopyAndAvailability();
		}
		renderChips();
		renderActions();
	};

	const loadMemberContext = () => {
		const member = getValue("member");
		if (!member) {
			state.member = null;
			applyState();
			return Promise.resolve();
		}

		return frappe.call("library_management.api.get_library_member_context", { member }).then((r) => {
			state.member = r.message.member;
			applyState();
		});
	};

	const loadCopyContext = () => {
		const scan_value = getValue("scan_value");
		const item = getValue("item");
		const member = getValue("member");

		if (!scan_value && !item) {
			state.copyPayload = null;
			applyState();
			return Promise.resolve();
		}

		return frappe.call("library_management.api.barcode_lookup", { scan_value, item, member }).then((r) => {
			state.copyPayload = r.message;
			state.copyMember = r.message.copy_member || null;
			if (scan_value && state.copyPayload?.copy?.current_member && ["Issued", "Overdue"].includes(state.copyPayload.copy.status)) {
				state.member = state.copyMember;
			} else if (r.message.member) {
				state.member = r.message.member;
			}
			applyState();
		}).catch((error) => {
			state.copyPayload = null;
			state.copyMember = null;
			applyState();
			renderFeedback(error?.message || __("Unable to load copy details."), "red");
		});
	};

	const scheduleAutoRefresh = () => {
		window.clearTimeout(state.autoRefreshTimer);
		state.autoRefreshTimer = window.setTimeout(() => {
			loadMemberContext().then(() => loadCopyContext());
		}, 220);
	};

	body.find("[data-action='issue']").on("click", () => {
		frappe.call("library_management.api.issue_library_copy", {
			member: getValue("member") || state.member?.name,
			scan_value: getValue("scan_value"),
			item: getValue("item")
		}).then((r) => {
			renderFeedback(__("Issued transaction {0} with due date {1}.", [r.message.name, r.message.due_date]), "green");
			scheduleAutoRefresh();
		});
	});

	body.find("[data-action='return']").on("click", () => {
		frappe.call("library_management.api.return_library_copy", {
			scan_value: getValue("scan_value") || state.copyPayload?.copy?.name,
			condition_status: getValue("condition_status"),
			notes: getValue("notes")
		}).then((r) => {
			renderFeedback(__("Returned transaction {0} with status {1}.", [r.message.name, r.message.status]), "green");
			scheduleAutoRefresh();
		});
	});

	body.find("[data-action='reserve']").on("click", () => {
		frappe.call("library_management.api.reserve_library_item", {
			member: getValue("member"),
			item: getValue("item")
		}).then((r) => {
			renderFeedback(__("Reservation {0} created successfully.", [r.message.name]), "orange");
			scheduleAutoRefresh();
		});
	});

	body.find("[data-action='clear']").on("click", () => {
		["member", "scan_value", "item", "notes"].forEach((fieldname) => setValue(fieldname, ""));
		setValue("condition_status", "Good");
		state.member = null;
		state.copyMember = null;
		state.copyPayload = null;
		lockMemberField(false);
		renderFeedback("");
		applyState();
	});

	controls.member.$input.on("change", () => {
		if (state.syncingFields) return;
		renderFeedback("");
		scheduleAutoRefresh();
	});

	controls.scan_value.$input.on("input change", () => {
		if (state.syncingFields) return;
		setValue("item", "");
		state.member = null;
		state.copyMember = null;
		state.copyPayload = null;
		setValue("member", "");
		lockMemberField(false);
		renderFeedback("");
		applyState();
		scheduleAutoRefresh();
	});

	controls.item.$input.on("change", () => {
		if (state.syncingFields) return;
		if (getValue("item")) {
			setValue("scan_value", "");
			lockMemberField(false);
		}
		renderFeedback("");
		scheduleAutoRefresh();
	});

	renderFeedback("");
	lockMemberField(false);
	applyState();
};
