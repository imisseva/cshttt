"""Leave application rules for Ling IELTS (Luồng 7).

- BR-LEAVE-05: chặn nộp đơn xin nghỉ trễ hơn 30 phút trước giờ bắt đầu buổi học.
- BR-LEAVE-06: chỉ giáo viên phụ trách lớp/buổi học mới được duyệt hoặc từ chối.
- Tự động ghi nhận custom_submitted_at, custom_processed_by và custom_processed_at.
"""
import frappe
from frappe import _
from frappe.utils import get_datetime, getdate, now_datetime

MIN_NOTICE_SECONDS = 30 * 60
PROCESSED_STATUSES = ("Chấp thuận", "Từ chối")


def _get_target_session_start(doc):
    """Trả về datetime bắt đầu buổi học sớm nhất liên quan đến đơn xin nghỉ."""
    if getattr(doc, "attendance_based_on", None) == "Course Schedule" and getattr(doc, "course_schedule", None):
        cs = frappe.db.get_value(
            "Course Schedule",
            doc.course_schedule,
            ["schedule_date", "from_time"],
            as_dict=True,
        )
        if cs and cs.schedule_date and cs.from_time is not None:
            return get_datetime(f"{cs.schedule_date} {cs.from_time}")
        return None

    if getattr(doc, "student_group", None) and getattr(doc, "from_date", None):
        to_date = getattr(doc, "to_date", None) or doc.from_date
        schedules = frappe.get_all(
            "Course Schedule",
            filters={
                "student_group": doc.student_group,
                "schedule_date": ["between", [doc.from_date, to_date]],
                "docstatus": ["<", 2],
            },
            fields=["schedule_date", "from_time"],
            order_by="schedule_date asc, from_time asc",
            limit_page_length=1,
        )
        if schedules and schedules[0].schedule_date and schedules[0].from_time is not None:
            return get_datetime(f"{schedules[0].schedule_date} {schedules[0].from_time}")

    return None


def _get_assigned_instructors(doc):
    """Lấy tập mã Instructor phụ trách lớp hoặc buổi học của đơn xin nghỉ."""
    instructors = set()
    student_group = getattr(doc, "student_group", None)

    if getattr(doc, "course_schedule", None):
        cs = frappe.db.get_value(
            "Course Schedule",
            doc.course_schedule,
            ["instructor", "student_group"],
            as_dict=True,
        )
        if cs:
            if cs.instructor:
                instructors.add(cs.instructor)
            if cs.student_group and not student_group:
                student_group = cs.student_group

    if student_group:
        group_instructors = frappe.get_all(
            "Student Group Instructor",
            filters={"parent": student_group, "parenttype": "Student Group"},
            pluck="instructor",
        )
        for inst in group_instructors:
            if inst:
                instructors.add(inst)

    return instructors


def is_assigned_instructor_user(doc, user):
    """True nếu user hiện tại là giáo viên phụ trách lớp/buổi học."""
    if not user or user == "Guest":
        return False

    assigned = _get_assigned_instructors(doc)
    if not assigned:
        return False

    user_lower = user.strip().lower()
    rows = frappe.get_all(
        "Instructor",
        filters={"name": ["in", sorted(assigned)]},
        fields=["name", "custom_email", "employee"],
    )
    for row in rows:
        if row.custom_email and row.custom_email.strip().lower() == user_lower:
            return True
        if row.employee:
            emp_user = frappe.db.get_value("Employee", row.employee, "user_id")
            if emp_user and emp_user.strip().lower() == user_lower:
                return True

    return False


def _enforce_lead_time(doc, reference_time):
    session_start = _get_target_session_start(doc)
    if session_start is not None:
        if (session_start - reference_time).total_seconds() < MIN_NOTICE_SECONDS:
            frappe.throw(
                _("Yêu cầu xin nghỉ phải được gửi trước giờ bắt đầu buổi học ít nhất 30 phút (BR-LEAVE-05).")
            )
    elif getattr(doc, "from_date", None) and getdate(doc.from_date) < getdate(reference_time):
        frappe.throw(
            _("Không thể gửi đơn xin nghỉ cho ngày đã qua (BR-LEAVE-05).")
        )


def _enforce_instructor_approval_permission(doc):
    if getattr(frappe.flags, "ignore_permissions", False):
        return
    if not is_assigned_instructor_user(doc, frappe.session.user):
        frappe.throw(
            _("Chỉ giáo viên phụ trách lớp/buổi học mới được phép duyệt hoặc từ chối đơn xin nghỉ (BR-LEAVE-06)."),
            frappe.PermissionError,
        )


def before_insert_student_leave(doc, method=None):
    """Tự động ghi thời điểm gửi đơn (Submitted At)."""
    if not getattr(doc, "custom_submitted_at", None):
        doc.custom_submitted_at = now_datetime()


def validate_student_leave(doc, method=None):
    """Kiểm tra BR-LEAVE-05, BR-LEAVE-06 và ghi nhận Submitted At / Processed By / Processed At."""
    now = now_datetime()
    is_new = doc.is_new()

    if not getattr(doc, "custom_submitted_at", None):
        doc.custom_submitted_at = now

    schedule_changed = not is_new and any(
        doc.has_value_changed(field)
        for field in ("attendance_based_on", "course_schedule", "student_group", "from_date", "to_date")
    )
    if is_new or schedule_changed:
        ref_time = now if schedule_changed else get_datetime(doc.custom_submitted_at)
        _enforce_lead_time(doc, ref_time)

    leave_status = getattr(doc, "custom_leave_status", None) or "Chờ duyệt"
    status_changed = is_new or doc.has_value_changed("custom_leave_status")

    if leave_status in PROCESSED_STATUSES:
        if status_changed:
            _enforce_instructor_approval_permission(doc)
            doc.custom_processed_by = frappe.session.user
            doc.custom_processed_at = now
    elif is_new:
        doc.custom_processed_by = None
        doc.custom_processed_at = None


def before_submit_student_leave(doc, method=None):
    """BR-LEAVE-06: Chỉ giáo viên phụ trách mới được Submit (duyệt) đơn xin nghỉ."""
    _enforce_instructor_approval_permission(doc)

    leave_status = getattr(doc, "custom_leave_status", None) or "Chờ duyệt"
    if leave_status == "Từ chối":
        frappe.throw(
            _("Không thể Submit đơn xin nghỉ đã chọn 'Từ chối' (Submit sẽ ghi nhận Vắng có phép). Hãy chỉ lưu bản nháp ở trạng thái 'Từ chối'.")
        )

    if leave_status == "Chờ duyệt":
        doc.custom_leave_status = "Chấp thuận"

    doc.custom_processed_by = frappe.session.user
    doc.custom_processed_at = now_datetime()
