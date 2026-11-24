app_name = "ling_ielts"
app_title = "Ling Ielts"
app_publisher = "Ling IELTS"
app_description = "Custom app for Ling IELTS on ERPNext Education"
app_email = "admin@lingielts.local"
app_license = "mit"

# Apps
# ------------------

required_apps = ["frappe", "erpnext", "education"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "ling_ielts",
		"logo": "/assets/ling_ielts/ling-logo.svg",
		"title": "Ling IELTS",
		"route": "/desk/ling-ielts",
		"has_permission": "ling_ielts.api.permission.has_app_permission",
	}
]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `ling_ielts/dock/ling_ielts/ling_ielts.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ling_ielts/css/ling_ielts.css"
# app_include_js = "/assets/ling_ielts/js/ling_ielts.js"

# include js, css files in header of web template
# web_include_css = "/assets/ling_ielts/css/ling_ielts.css"
# web_include_js = "/assets/ling_ielts/js/ling_ielts.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ling_ielts/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Course Schedule": "public/js/course_schedule.js",
	"Student Group": "public/js/student_group.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ling_ielts/public/icons.svg"

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
# 	"methods": "ling_ielts.utils.jinja_methods",
# 	"filters": "ling_ielts.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ling_ielts.install.before_install"
# after_install = "ling_ielts.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ling_ielts.uninstall.before_uninstall"
# after_uninstall = "ling_ielts.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ling_ielts.utils.before_app_install"
# after_app_install = "ling_ielts.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ling_ielts.utils.before_app_uninstall"
# after_app_uninstall = "ling_ielts.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "ling_ielts.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "ling_ielts.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ling_ielts.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["ling_ielts.search.awesomebar_results"]

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

doc_events = {
	"Course Schedule": {
		"validate": [
			"ling_ielts.ling_scheduling.validate_course_schedule",
			"ling_ielts.ling_room.validate_course_schedule_room",
		]
	},
	"Fees": {
		"validate": "ling_ielts.ling_fees.validate_fees_discount"
	},
	"Student Group": {
		"validate": "ling_ielts.ling_fees.validate_student_group_fees"
	},
	"Student Leave Application": {
		"before_insert": "ling_ielts.ling_leave.before_insert_student_leave",
		"before_validate": "ling_ielts.ling_leave.validate_student_leave",
		"before_submit": "ling_ielts.ling_leave.before_submit_student_leave",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ling_ielts.tasks.all"
# 	],
# 	"daily": [
# 		"ling_ielts.tasks.daily"
# 	],
# 	"hourly": [
# 		"ling_ielts.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ling_ielts.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ling_ielts.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ling_ielts.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "ling_ielts.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ling_ielts.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ling_ielts.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ling_ielts.utils.before_request"]
# after_request = ["ling_ielts.utils.after_request"]

# Job Events
# ----------
# before_job = ["ling_ielts.utils.before_job"]
# after_job = ["ling_ielts.utils.after_job"]

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
# 	"ling_ielts.auth.validate"
# ]

# on_social_login = "ling_ielts.auth.on_social_login"

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

