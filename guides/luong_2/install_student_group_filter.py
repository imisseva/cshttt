"""Run with bench's Python from the sites directory to install the UI filter fix."""
import json
from datetime import datetime
from pathlib import Path

import frappe


site = "school.localhost"
script_name = "Ling IELTS - Student Group Instructor Filter"
source = Path(__file__).with_name("student_group_instructor_filter.client.js")

frappe.init(site=site)
frappe.connect()
try:
    frappe.set_user("Administrator")
    if frappe.db.exists("Client Script", script_name):
        doc = frappe.get_doc("Client Script", script_name)
        backup_dir = Path(frappe.get_site_path("private", "backups"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup = backup_dir / f"student_group_instructor_filter_{stamp}.json"
        backup.write_text(frappe.as_json(doc.as_dict()), encoding="utf-8")
        print(f"Previous Client Script saved to {backup}")
    else:
        doc = frappe.new_doc("Client Script")
        doc.name = script_name

    doc.dt = "Student Group"
    doc.view = "Form"
    doc.enabled = 1
    doc.script = source.read_text(encoding="utf-8")
    doc.save()
    frappe.db.commit()

    saved = frappe.get_doc("Client Script", script_name)
    assert saved.enabled and saved.dt == "Student Group"
    assert saved.script == source.read_text(encoding="utf-8")
    print(json.dumps({"client_script": saved.name, "doctype": saved.dt,
                      "enabled": saved.enabled}, ensure_ascii=False))
except Exception:
    frappe.db.rollback()
    raise
finally:
    frappe.destroy()
