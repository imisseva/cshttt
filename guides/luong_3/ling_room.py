"""Room type filter and save validation for the Ling IELTS room allocation flow.

Luồng 3 - Phân bổ phòng học:
  - room_query: lọc danh sách phòng theo loại yêu cầu của môn học (BR-ROOM-02).
  - validate_course_schedule_room: chặn lưu khi phòng không đúng loại yêu cầu.
Quy tắc chặn trùng phòng (BR-ROOM-01) đã có sẵn trong CourseSchedule.validate_overlap().
"""
from frappe import _
import frappe
from frappe.utils import cint


def get_required_room_type(course):
    """Trả về loại phòng mà môn học yêu cầu, hoặc None khi chưa thiết lập."""
    if not course:
        return None
    return frappe.db.get_value("Course", course, "custom_required_room_type") or None


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def room_query(doctype, txt, searchfield, start, page_len, filters):
    """Tìm kiếm phòng học, giới hạn theo loại phòng mà Course yêu cầu."""
    if doctype != "Room":
        frappe.throw(_("Loại dữ liệu tìm kiếm không hợp lệ."))
    if not (
        frappe.has_permission("Course Schedule", "create")
        or frappe.has_permission("Course Schedule", "write")
    ):
        frappe.throw(_("Bạn chưa có quyền xếp lịch."), frappe.PermissionError)

    filters = frappe.parse_json(filters) or {}
    required = get_required_room_type(filters.get("course"))

    conditions = {}
    if required:
        conditions["custom_room_type"] = required

    rooms = frappe.get_list(
        "Room",
        filters=conditions,
        or_filters={
            "name": ["like", f"%{txt}%"],
            "room_name": ["like", f"%{txt}%"],
        },
        fields=["name", "room_name"],
        order_by="room_name asc, name asc",
        limit_page_length=0,
    )

    offset = max(0, cint(start))
    page_size = min(100, max(1, cint(page_len) or 20))
    return [[room.name, room.room_name] for room in rooms][offset : offset + page_size]


def validate_course_schedule_room(doc, method=None):
    """BR-ROOM-02: phòng được chọn phải đúng loại yêu cầu của buổi học."""
    if not doc.course or not doc.room:
        return

    required = get_required_room_type(doc.course)
    if not required:
        return

    actual = frappe.db.get_value("Room", doc.room, "custom_room_type")
    if actual != required:
        frappe.throw(
            _("Phòng {0} có loại '{1}' nhưng buổi học yêu cầu loại '{2}' (BR-ROOM-02). Hãy chọn phòng đúng loại.").format(
                doc.room, actual or _("Chưa phân loại"), required
            )
        )
