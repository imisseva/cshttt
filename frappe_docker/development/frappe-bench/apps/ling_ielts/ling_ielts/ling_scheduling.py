"""Instructor selection and save validation for the Ling IELTS scheduling flow."""
from datetime import time

import frappe
from frappe import _
from frappe.utils import cint, getdate, get_time


def normalize_window(schedule_date, from_time, to_time):
    if any(value in (None, "") for value in (schedule_date, from_time, to_time)):
        frappe.throw(_("Hãy chọn ngày học, giờ bắt đầu và giờ kết thúc."))

    date = getdate(schedule_date)
    start = get_time(from_time)
    end = get_time(to_time)
    if not time.min <= start < end <= time.max:
        frappe.throw(_("Giờ kết thúc phải sau giờ bắt đầu trong cùng một ngày."))
    return date, start, end


def get_group_context(student_group):
    group = frappe.get_doc("Student Group", student_group)
    group.check_permission("read")
    if not group.program:
        frappe.throw(_("Hãy chọn Program cho lớp trong Student Group."))

    assigned = {row.instructor for row in group.instructors if row.instructor}
    if not assigned:
        frappe.throw(_("Hãy phân công giáo viên trong bảng Instructors của Student Group."))
    return group.program, assigned


AVAILABILITY_SQL = """
    SELECT name
    FROM `tabInstructor Availability`
    WHERE instructor = %(instructor)s
      AND available_date = %(schedule_date)s
      AND program = %(program)s
      AND from_time <= %(from_time)s
      AND to_time >= %(to_time)s
      AND docstatus < 2
    LIMIT 1
"""

COURSE_CONFLICT_SQL = """
    SELECT name
    FROM `tabCourse Schedule`
    WHERE instructor = %(instructor)s
      AND schedule_date = %(schedule_date)s
      AND docstatus < 2
      AND name != %(current_schedule)s
      AND from_time < %(to_time)s
      AND to_time > %(from_time)s
    LIMIT 1
"""

ASSESSMENT_CONFLICT_SQL = """
    SELECT name
    FROM `tabAssessment Plan`
    WHERE (supervisor = %(instructor)s OR examiner = %(instructor)s)
      AND schedule_date = %(schedule_date)s
      AND docstatus < 2
      AND from_time < %(to_time)s
      AND to_time > %(from_time)s
    LIMIT 1
"""


def is_available(parameters, *, lock=False):
    # Locking reads see the latest committed bookings when validating a save.
    suffix = " FOR UPDATE" if lock else ""
    if not frappe.db.sql(AVAILABILITY_SQL + suffix, parameters):
        return False
    if frappe.db.sql(COURSE_CONFLICT_SQL + suffix, parameters):
        return False
    return not frappe.db.sql(ASSESSMENT_CONFLICT_SQL + suffix, parameters)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def instructor_query(doctype, txt, searchfield, start, page_len, filters):
    if doctype != "Instructor":
        frappe.throw(_("Loại dữ liệu tìm kiếm không hợp lệ."))
    if not (
        frappe.has_permission("Course Schedule", "create")
        or frappe.has_permission("Course Schedule", "write")
    ):
        frappe.throw(_("Bạn chưa có quyền xếp lịch."), frappe.PermissionError)
    if not frappe.has_permission("Instructor Availability", "read"):
        frappe.throw(_("Bạn cần quyền đọc Instructor Availability."), frappe.PermissionError)

    filters = frappe.parse_json(filters) or {}
    required = ("student_group", "schedule_date", "from_time", "to_time")
    if any(filters.get(field) in (None, "") for field in required):
        return []

    date, from_time, to_time = normalize_window(
        filters["schedule_date"], filters["from_time"], filters["to_time"]
    )
    program, assigned = get_group_context(filters["student_group"])

    current_schedule = filters.get("current_schedule") or ""
    if current_schedule:
        frappe.get_doc("Course Schedule", current_schedule).check_permission("write")

    teachers = frappe.get_list(
        "Instructor",
        filters={"name": ["in", sorted(assigned)], "status": "Active"},
        or_filters={"name": ["like", f"%{txt}%"], "instructor_name": ["like", f"%{txt}%"]},
        fields=["name", "instructor_name"],
        order_by="instructor_name asc, name asc",
        limit_page_length=0,
    )
    available = []
    for teacher in teachers:
        parameters = {
            "instructor": teacher.name,
            "program": program,
            "schedule_date": date,
            "from_time": from_time,
            "to_time": to_time,
            "current_schedule": current_schedule,
        }
        if is_available(parameters):
            available.append([teacher.name, teacher.instructor_name])

    offset = max(0, cint(start))
    page_size = min(100, max(1, cint(page_len) or 20))
    return available[offset : offset + page_size]


def validate_course_schedule(doc, method=None):
    scheduling_fields = ("student_group", "schedule_date", "from_time", "to_time", "instructor")
    if not doc.is_new() and not any(doc.has_value_changed(field) for field in scheduling_fields):
        return

    if not doc.student_group or not doc.instructor:
        frappe.throw(_("Hãy chọn lớp và giáo viên trước khi lưu lịch."))
    date, from_time, to_time = normalize_window(doc.schedule_date, doc.from_time, doc.to_time)
    program, assigned = get_group_context(doc.student_group)
    if doc.instructor not in assigned:
        frappe.throw(_("Giáo viên chưa được phân công cho lớp này."))

    # A shared Instructor lock serializes saves through this Course Schedule hook.
    teacher = frappe.db.sql(
        "SELECT status FROM `tabInstructor` WHERE name = %s FOR UPDATE",
        (doc.instructor,),
        as_dict=True,
    )
    if not teacher or teacher[0].status != "Active":
        frappe.throw(_("Giáo viên phải có trạng thái Active."))

    parameters = {
        "instructor": doc.instructor,
        "program": program,
        "schedule_date": date,
        "from_time": from_time,
        "to_time": to_time,
        "current_schedule": doc.name if not doc.is_new() else "",
    }
    if not is_available(parameters, lock=True):
        frappe.throw(
            _("Giáo viên chưa đăng ký giờ rảnh cho cấp này hoặc đã có lịch trùng. Hãy chọn lại giáo viên/khung giờ.")
        )
