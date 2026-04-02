app_name = "library_management"
app_title = "Library Management"
app_publisher = "Sahil"
app_description = "Production-ready library management for ERPNext"
app_email = "admin@sahil.com"
app_license = "mit"
app_home = "/app/library-management"
app_logo_url = "/assets/frappe/images/frappe-framework-logo.svg"

add_to_apps_screen = [
    {
        "name": "library_management",
        "logo": "/assets/frappe/images/frappe-framework-logo.svg",
        "title": "Library Management",
        "route": "/app/library-management",
    }
]

fixtures = [
    {
        "dt": "Role",
        "filters": {
            "name": ["in", ["Library Manager", "Librarian", "Library Assistant", "Library Member"]]
        },
    },
    {
        "dt": "Custom Field",
        "filters": {
            "name": [
                "in",
                [
                    "Item-library_section",
                    "Item-library_is_catalog_item",
                    "Item-library_material_type",
                    "Item-library_is_reference_only",
                    "Item-library_is_borrowable",
                    "Item-library_default_loan_period",
                    "Item-library_isbn_10",
                    "Item-library_isbn_13",
                    "Item-library_authors",
                    "Item-library_publisher",
                    "Item-library_edition",
                    "Item-library_language",
                    "Item-library_publication_year",
                    "Item-library_subject",
                    "Item-library_classification_code",
                    "Item-library_keywords",
                    "Item-library_summary",
                    "Item-library_front_cover",
                    "Item-library_back_cover",
                    "Sales Invoice-library_member",
                    "Sales Invoice-library_transaction",
                    "Sales Invoice-library_fine",
                ],
            ]
        },
    },
]

after_install = "library_management.install.after_install"

scheduler_events = {
    "daily": [
        "library_management.services.circulation.refresh_overdues",
        "library_management.services.reservation.expire_stale_reservations",
        "library_management.services.member.expire_memberships",
    ]
}

permission_query_conditions = {
    "Library Member": "library_management.permissions.get_library_member_permission_query",
    "Library Transaction": "library_management.permissions.get_library_transaction_permission_query",
    "Library Reservation": "library_management.permissions.get_library_reservation_permission_query",
    "Library Fine": "library_management.permissions.get_library_fine_permission_query",
}

has_permission = {
    "Library Member": "library_management.permissions.has_library_member_permission",
    "Library Transaction": "library_management.permissions.has_library_transaction_permission",
    "Library Reservation": "library_management.permissions.has_library_reservation_permission",
    "Library Fine": "library_management.permissions.has_library_fine_permission",
}

doc_events = {
    "Purchase Receipt": {
        "on_submit": "library_management.services.procurement.on_purchase_receipt_submit",
    }
}

standard_portal_menu_items = [
    {
        "title": "My Library Loans",
        "route": "/library/my-loans",
        "reference_doctype": "Library Transaction",
        "role": "Library Member",
    },
    {
        "title": "My Library Reservations",
        "route": "/library/my-reservations",
        "reference_doctype": "Library Reservation",
        "role": "Library Member",
    },
]

website_route_rules = [
    {"from_route": "/library/my-loans", "to_route": "library/my_loans"},
    {"from_route": "/library/my-reservations", "to_route": "library/my_reservations"},
]

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "sahil_library",
# 		"logo": "/assets/sahil_library/logo.png",
# 		"title": "Sahil Library",
# 		"route": "/sahil_library",
# 		"has_permission": "sahil_library.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sahil_library/css/sahil_library.css"
# app_include_js = "/assets/sahil_library/js/sahil_library.js"

# include js, css files in header of web template
# web_include_css = "/assets/sahil_library/css/sahil_library.css"
# web_include_js = "/assets/sahil_library/js/sahil_library.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sahil_library/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sahil_library/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sahil_library.utils.jinja_methods",
# 	"filters": "sahil_library.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sahil_library.install.before_install"
# after_install = "sahil_library.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sahil_library.uninstall.before_uninstall"
# after_uninstall = "sahil_library.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sahil_library.utils.before_app_install"
# after_app_install = "sahil_library.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sahil_library.utils.before_app_uninstall"
# after_app_uninstall = "sahil_library.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sahil_library.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sahil_library.tasks.all"
# 	],
# 	"daily": [
# 		"sahil_library.tasks.daily"
# 	],
# 	"hourly": [
# 		"sahil_library.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sahil_library.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sahil_library.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sahil_library.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "sahil_library.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sahil_library.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sahil_library.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sahil_library.utils.before_request"]
# after_request = ["sahil_library.utils.after_request"]

# Job Events
# ----------
# before_job = ["sahil_library.utils.before_job"]
# after_job = ["sahil_library.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sahil_library.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
