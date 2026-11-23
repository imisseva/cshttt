import frappe


def has_app_permission():
	"""Allow all authenticated Desk users to access the Ling IELTS app."""
	return frappe.session.user != "Guest"
