# Copyright (c) 2026, Ling IELTS and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, get_datetime, get_time, getdate, now_datetime

from ling_ielts.ling_room import get_required_room_type
from ling_ielts.ling_scheduling import is_available

EMERGENCY_THRESHOLD_SECONDS = 24 * 3600


def _to_time(val):
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        return get_time(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    return get_time(val)


def _time_to_str(val):
    return _to_time(val).strftime("%H:%M:%S")


def _time_diff_td(start_val, end_val):
    s = _to_time(start_val)
    e = _to_time(end_val)
    dt_s = datetime.combine(datetime.today().date(), s)
    dt_e = datetime.combine(datetime.today().date(), e)
    return dt_e - dt_s


def _get_term_bounds(student_group, reference_date):
    ref = getdate(reference_date)
    if student_group and frappe.db.exists("Student Group", student_group):
        grp = frappe.db.get_value(
            "Student Group", student_group, ["academic_term", "academic_year"], as_dict=True
        )
        if grp and grp.academic_term:
            term = frappe.db.get_value(
                "Academic Term",
                grp.academic_term,
                ["term_start_date", "term_end_date"],
                as_dict=True,
            )
            if term and term.term_start_date and term.term_end_date:
                return getdate(term.term_start_date), getdate(term.term_end_date)
        if grp and grp.academic_year:
            year = frappe.db.get_value(
                "Academic Year",
                grp.academic_year,
                ["year_start_date", "year_end_date"],
                as_dict=True,
            )
            if year and year.year_start_date and year.year_end_date:
                return getdate(year.year_start_date), getdate(year.year_end_date)

    return ref, add_days(ref, 90)


def _has_student_group_conflict(student_group, schedule_date, from_time, to_time, exclude_cs=""):
    params = {
        "student_group": student_group,
        "schedule_date": schedule_date,
        "from_time": from_time,
        "to_time": to_time,
        "exclude_cs": exclude_cs or "",
    }
    if frappe.db.sql(
        """
        SELECT name FROM `tabCourse Schedule`
        WHERE student_group = %(student_group)s
          AND schedule_date = %(schedule_date)s
          AND docstatus < 2
          AND name != %(exclude_cs)s
          AND from_time < %(to_time)s
          AND to_time > %(from_time)s
        LIMIT 1
        """,
        params,
    ):
        return True

    return bool(
        frappe.db.sql(
            """
            SELECT name FROM `tabAssessment Plan`
            WHERE student_group = %(student_group)s
              AND schedule_date = %(schedule_date)s
              AND docstatus < 2
              AND from_time < %(to_time)s
              AND to_time > %(from_time)s
            LIMIT 1
            """,
            params,
        )
    )


def _find_free_rooms(course, schedule_date, from_time, to_time, exclude_cs=""):
    required_type = get_required_room_type(course)
    filters = {"custom_room_type": required_type} if required_type else {}
    rooms = frappe.get_all(
        "Room",
        filters=filters,
        fields=["name", "room_name"],
        order_by="room_name asc, name asc",
    )
    free = []
    for room in rooms:
        params = {
            "room": room.name,
            "schedule_date": schedule_date,
            "from_time": from_time,
            "to_time": to_time,
            "exclude_cs": exclude_cs or "",
        }
        cs_conflict = frappe.db.sql(
            """
            SELECT name FROM `tabCourse Schedule`
            WHERE room = %(room)s
              AND schedule_date = %(schedule_date)s
              AND docstatus < 2
              AND name != %(exclude_cs)s
              AND from_time < %(to_time)s
              AND to_time > %(from_time)s
            LIMIT 1
            """,
            params,
        )
        if cs_conflict:
            continue
        ap_conflict = frappe.db.sql(
            """
            SELECT name FROM `tabAssessment Plan`
            WHERE room = %(room)s
              AND schedule_date = %(schedule_date)s
              AND docstatus < 2
              AND from_time < %(to_time)s
              AND to_time > %(from_time)s
            LIMIT 1
            """,
            params,
        )
        if ap_conflict:
            continue
        free.append({"room": room.name, "room_name": room.room_name or room.name})
    return free


def _instructor_matches_program(teaching_levels, program):
    if not teaching_levels or not program:
        return True
    levels_lower = teaching_levels.lower()
    prog_lower = program.lower()
    if prog_lower in levels_lower:
        return True
    # Khớp theo các band số trong tên Program (ví dụ "IELTS 5.0–5.5" -> "5.0", "5.5")
    for token in prog_lower.replace("–", " ").replace("-", " ").split():
        if any(ch.isdigit() for ch in token) and token in levels_lower:
            return True
    return False


def _generate_candidate_windows(avail_from, avail_to, duration_td):
    """Sinh các khung giờ độ dài bằng buổi gốc nằm trong khoảng rảnh."""
    base_date = datetime.today().date()
    start_dt = datetime.combine(base_date, _to_time(avail_from))
    end_dt = datetime.combine(base_date, _to_time(avail_to))
    if duration_td <= timedelta(0) or start_dt + duration_td > end_dt:
        return []

    windows = []
    cursor = start_dt
    step = timedelta(minutes=30)
    while cursor + duration_td <= end_dt:
        windows.append((cursor.time(), (cursor + duration_td).time()))
        cursor += step
    return windows


class InstructorRescheduleRequest(Document):
    def validate(self):
        self._sync_course_schedule_details()
        self._validate_instructor_ownership()
        self._update_emergency_flag()
        self._update_approval_audit_fields()

    def before_submit(self):
        if self.status not in ("Chấp thuận", "Từ chối"):
            frappe.throw(
                _("Vui lòng chọn Trạng thái duyệt ('Chấp thuận' hoặc 'Từ chối') trước khi Submit (BR-TCH-02).")
            )

        if self.status == "Chấp thuận":
            if not self.resolution_type:
                frappe.throw(_("Vui lòng chọn Phương án xử lý trước khi Submit."))

            if self.resolution_type == "Đổi giáo viên":
                if not self.replacement_instructor:
                    frappe.throw(_("Vui lòng chọn Giáo viên dạy thay."))
                if self.replacement_instructor == self.instructor:
                    frappe.throw(_("Giáo viên dạy thay phải khác giáo viên ban đầu."))
            elif self.resolution_type in ("Lùi lịch", "Dạy bù", "Dạy bù online"):
                if not (self.new_schedule_date and self.new_from_time and self.new_to_time):
                    frappe.throw(_("Vui lòng nhập đầy đủ Ngày mới, Từ giờ mới và Đến giờ mới."))
                if _to_time(self.new_from_time) >= _to_time(self.new_to_time):
                    frappe.throw(_("Giờ kết thúc mới phải sau giờ bắt đầu mới."))
                if self.resolution_type in ("Lùi lịch", "Dạy bù") and not self.new_room:
                    orig_room = frappe.db.get_value("Course Schedule", self.course_schedule, "room")
                    if orig_room:
                        self.new_room = orig_room
                    else:
                        frappe.throw(_("Vui lòng chọn Phòng học mới."))

        self.approved_by = frappe.session.user
        self.thời_điểm_duyệt = now_datetime()

    def on_submit(self):
        if self.status != "Chấp thuận":
            return

        cs = frappe.get_doc("Course Schedule", self.course_schedule)

        if self.resolution_type == "Lùi lịch":
            cs.schedule_date = self.new_schedule_date
            cs.from_time = self.new_from_time
            cs.to_time = self.new_to_time
            if self.new_room:
                cs.room = self.new_room
            cs.custom_session_status = "Đã dời lịch"
            cs.save(ignore_permissions=True)

        elif self.resolution_type == "Đổi giáo viên":
            self._ensure_instructor_assigned_to_group(cs.student_group, self.replacement_instructor)
            cs.instructor = self.replacement_instructor
            cs.custom_session_status = "Đã xếp"
            cs.save(ignore_permissions=True)

        elif self.resolution_type == "Dạy bù":
            cs.db_set("custom_session_status", "Nghỉ - chờ bù")
            makeup = frappe.get_doc(
                {
                    "doctype": "Course Schedule",
                    "student_group": cs.student_group,
                    "instructor": self.instructor,
                    "course": cs.course,
                    "program": cs.program,
                    "schedule_date": self.new_schedule_date,
                    "from_time": self.new_from_time,
                    "to_time": self.new_to_time,
                    "room": self.new_room or cs.room,
                    "custom_is_online": 0,
                    "custom_session_status": "Dạy bù",
                }
            )
            makeup.insert(ignore_permissions=True)
            self.db_set("makeup_course_schedule", makeup.name)

        elif self.resolution_type == "Dạy bù online":
            cs.db_set("custom_session_status", "Nghỉ - chờ bù")
            makeup = frappe.get_doc(
                {
                    "doctype": "Course Schedule",
                    "student_group": cs.student_group,
                    "instructor": self.instructor,
                    "course": cs.course,
                    "program": cs.program,
                    "schedule_date": self.new_schedule_date,
                    "from_time": self.new_from_time,
                    "to_time": self.new_to_time,
                    "room": None,
                    "custom_is_online": 1,
                    "custom_session_status": "Dạy bù",
                }
            )
            makeup.insert(ignore_permissions=True)
            self.db_set("makeup_course_schedule", makeup.name)

    def on_cancel(self):
        if self.makeup_course_schedule and frappe.db.exists("Course Schedule", self.makeup_course_schedule):
            self.db_set("makeup_course_schedule", None)

    def _sync_course_schedule_details(self):
        if not self.course_schedule:
            return
        cs = frappe.db.get_value(
            "Course Schedule",
            self.course_schedule,
            ["student_group", "program", "schedule_date", "from_time", "to_time", "instructor"],
            as_dict=True,
        )
        if not cs:
            return
        self.student_group = cs.student_group
        self.program = cs.program
        self.schedule_date = cs.schedule_date
        self.from_time = cs.from_time
        self.to_time = cs.to_time

    def _validate_instructor_ownership(self):
        if not self.course_schedule or not self.instructor:
            return
        cs_instructor = frappe.db.get_value("Course Schedule", self.course_schedule, "instructor")
        if cs_instructor and cs_instructor != self.instructor:
            frappe.throw(
                _("Buổi học {0} được phân công cho giáo viên '{1}', không phải '{2}'.").format(
                    self.course_schedule, cs_instructor, self.instructor
                )
            )

    def _update_emergency_flag(self):
        if not self.requested_at:
            self.requested_at = now_datetime()
        if not self.schedule_date or self.from_time is None:
            return
        session_start = get_datetime(f"{self.schedule_date} {_time_to_str(self.from_time)}")
        req_dt = get_datetime(self.requested_at)
        self.is_emergency = 1 if (session_start - req_dt).total_seconds() < EMERGENCY_THRESHOLD_SECONDS else 0

    def _update_approval_audit_fields(self):
        if self.status in ("Chấp thuận", "Từ chối"):
            if not self.approved_by or self.has_value_changed("status"):
                self.approved_by = frappe.session.user
                self.thời_điểm_duyệt = now_datetime()
        elif self.is_new():
            self.approved_by = None
            self.thời_điểm_duyệt = None

    def _ensure_instructor_assigned_to_group(self, student_group, instructor):
        if not student_group or not instructor:
            return
        sg = frappe.get_doc("Student Group", student_group)
        assigned = {row.instructor for row in sg.instructors if row.instructor}
        if instructor not in assigned:
            sg.append("instructors", {"instructor": instructor})
            sg.flags.skip_ling_fee_check = True
            sg.save(ignore_permissions=True)


@frappe.whitelist()
def get_reschedule_suggestions(course_schedule=None, instructor=None, request_name=None):
    """BR-TCH-03: Gợi ý 4 phương án ưu tiên khi giáo viên xin nghỉ 1 buổi.

    Thứ tự ưu tiên:
      1. Lùi lịch sang khung giờ khác trong tuần (không kéo dài khóa).
      2. Đổi giáo viên khác đủ cấp độ dạy thay đúng buổi đó.
      3. Dạy bù vào buổi trống khác còn trong thời gian khóa (có phòng phù hợp).
      4. Dạy bù online (khi không có phòng phù hợp hoặc cần phương án trực tuyến).
    """
    if request_name and frappe.db.exists("Instructor Reschedule Request", request_name):
        req_doc = frappe.get_doc("Instructor Reschedule Request", request_name)
        req_doc.check_permission("read")
        course_schedule = course_schedule or req_doc.course_schedule
        instructor = instructor or req_doc.instructor

    if not course_schedule or not frappe.db.exists("Course Schedule", course_schedule):
        frappe.throw(_("Vui lòng chọn Buổi học cần nghỉ hợp lệ."))

    cs = frappe.get_doc("Course Schedule", course_schedule)
    cs.check_permission("read")
    orig_instructor = instructor or cs.instructor
    orig_date = getdate(cs.schedule_date)
    orig_from = _to_time(cs.from_time)
    orig_to = _to_time(cs.to_time)
    duration_td = _time_diff_td(orig_from, orig_to)
    program = cs.program or frappe.db.get_value("Student Group", cs.student_group, "program")

    today_date = getdate(now_datetime())
    term_start, term_end = _get_term_bounds(cs.student_group, orig_date)
    search_start = max(today_date, term_start)

    # Tuần chứa buổi học gốc (Thứ 2 -> Chủ nhật), giới hạn trong kỳ học
    week_monday = add_days(orig_date, -orig_date.weekday())
    week_sunday = add_days(week_monday, 6)
    week_start = max(search_start, week_monday)
    week_end = min(term_end, week_sunday)

    # Lấy toàn bộ giờ rảnh của giáo viên gốc trong thời gian khóa
    avails = frappe.get_all(
        "Instructor Availability",
        filters={
            "instructor": orig_instructor,
            "program": program,
            "available_date": ["between", [search_start, term_end]],
            "docstatus": ["<", 2],
        },
        fields=["available_date", "from_time", "to_time"],
        order_by="available_date asc, from_time asc",
    )

    priority_1_reschedule = []
    priority_3_makeup = []
    priority_4_online = []
    seen_slots = set()

    for av in avails:
        av_date = getdate(av.available_date)
        for cand_from, cand_to in _generate_candidate_windows(av.from_time, av.to_time, duration_td):
            if av_date == orig_date and cand_from == orig_from and cand_to == orig_to:
                continue

            slot_key = (str(av_date), cand_from.strftime("%H:%M:%S"), cand_to.strftime("%H:%M:%S"))
            if slot_key in seen_slots:
                continue
            seen_slots.add(slot_key)

            params = {
                "instructor": orig_instructor,
                "program": program,
                "schedule_date": av_date,
                "from_time": cand_from,
                "to_time": cand_to,
                "current_schedule": cs.name,
            }
            if not is_available(params):
                continue
            if _has_student_group_conflict(cs.student_group, av_date, cand_from, cand_to, exclude_cs=cs.name):
                continue

            free_rooms = _find_free_rooms(cs.course, av_date, cand_from, cand_to, exclude_cs=cs.name)
            slot_payload = {
                "schedule_date": str(av_date),
                "from_time": cand_from.strftime("%H:%M:%S"),
                "to_time": cand_to.strftime("%H:%M:%S"),
            }

            if free_rooms:
                chosen_room = free_rooms[0]
                offline_option = {
                    **slot_payload,
                    "room": chosen_room["room"],
                    "room_name": chosen_room["room_name"],
                    "available_rooms_count": len(free_rooms),
                }
                if week_start <= av_date <= week_end:
                    priority_1_reschedule.append({**offline_option, "resolution_type": "Lùi lịch"})
                else:
                    priority_3_makeup.append({**offline_option, "resolution_type": "Dạy bù"})
            else:
                priority_4_online.append({**slot_payload, "resolution_type": "Dạy bù online"})

    # Nếu chưa có slot online riêng do thiếu phòng, vẫn gợi ý các khung giờ rảnh hợp lệ để dạy bù online
    if not priority_4_online:
        for opt in (priority_3_makeup or priority_1_reschedule)[:3]:
            priority_4_online.append(
                {
                    "resolution_type": "Dạy bù online",
                    "schedule_date": opt["schedule_date"],
                    "from_time": opt["from_time"],
                    "to_time": opt["to_time"],
                }
            )

    # Priority 2: Đổi giáo viên khác cùng cấp độ & rảnh đúng buổi gốc
    priority_2_substitute = []
    group_instructors = set(
        frappe.get_all(
            "Student Group Instructor",
            filters={"parent": cs.student_group, "parenttype": "Student Group"},
            pluck="instructor",
        )
    )
    active_instructors = frappe.get_all(
        "Instructor",
        filters={"status": "Active", "name": ["!=", orig_instructor]},
        fields=["name", "instructor_name", "custom_teaching_levels"],
        order_by="instructor_name asc, name asc",
    )
    for teacher in active_instructors:
        in_group = teacher.name in group_instructors
        if not in_group and not _instructor_matches_program(teacher.custom_teaching_levels, program):
            continue
        params = {
            "instructor": teacher.name,
            "program": program,
            "schedule_date": orig_date,
            "from_time": orig_from,
            "to_time": orig_to,
            "current_schedule": cs.name,
        }
        if is_available(params):
            priority_2_substitute.append(
                {
                    "resolution_type": "Đổi giáo viên",
                    "instructor": teacher.name,
                    "instructor_name": teacher.instructor_name or teacher.name,
                    "assigned_in_group": in_group,
                }
            )
    priority_2_substitute.sort(key=lambda item: (not item["assigned_in_group"], item["instructor_name"]))

    recommended_priority = 4
    recommended_type = "Dạy bù online"
    if priority_1_reschedule:
        recommended_priority = 1
        recommended_type = "Lùi lịch"
    elif priority_2_substitute:
        recommended_priority = 2
        recommended_type = "Đổi giáo viên"
    elif priority_3_makeup:
        recommended_priority = 3
        recommended_type = "Dạy bù"

    return {
        "course_schedule": cs.name,
        "student_group": cs.student_group,
        "program": program,
        "term_start": str(term_start),
        "term_end": str(term_end),
        "week_start": str(week_monday),
        "week_end": str(week_sunday),
        "recommended_priority": recommended_priority,
        "recommended_type": recommended_type,
        "priorities": [
            {
                "priority": 1,
                "resolution_type": "Lùi lịch",
                "label": _("1. Lùi lịch trong tuần (không kéo dài khóa)"),
                "options": priority_1_reschedule,
            },
            {
                "priority": 2,
                "resolution_type": "Đổi giáo viên",
                "label": _("2. Đổi giáo viên khác cùng cấp độ dạy thay đúng buổi"),
                "options": priority_2_substitute,
            },
            {
                "priority": 3,
                "resolution_type": "Dạy bù",
                "label": _("3. Dạy bù vào buổi trống khác trong thời gian khóa"),
                "options": priority_3_makeup,
            },
            {
                "priority": 4,
                "resolution_type": "Dạy bù online",
                "label": _("4. Dạy bù online (khi không có phòng trực tiếp phù hợp)"),
                "options": priority_4_online,
            },
        ],
    }
