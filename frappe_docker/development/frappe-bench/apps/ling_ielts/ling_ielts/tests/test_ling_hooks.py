"""Kiểm thử tự động các Python Hooks & Controllers của ling_ielts.

Chạy trong container Frappe từ thư mục sites:
    docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 \
        /workspace/development/frappe-bench/env/bin/python \
        /workspace/development/frappe-bench/apps/ling_ielts/ling_ielts/tests/test_ling_hooks.py
"""
import os
import sys
from datetime import timedelta

import frappe
from frappe.utils import add_days, get_datetime, now_datetime, today

site = "school.localhost"
frappe.init(site=site)
frappe.connect()

bench_path = frappe.utils.get_bench_path()
education_parent = os.path.join(bench_path, "apps", "education")
if education_parent not in sys.path:
    sys.path.insert(0, education_parent)

PASSED = 0
FAILED = 0
CREATED = []


def check(label, condition):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}")
    else:
        FAILED += 1
        print(f"  [FAIL] {label}")


def expect_error(label, exc_type, fn, contains=None):
    global PASSED, FAILED
    try:
        fn()
    except exc_type as exc:
        if contains and contains not in str(exc):
            FAILED += 1
            print(f"  [FAIL] {label} (lỗi không chứa '{contains}': {exc})")
        else:
            PASSED += 1
            print(f"  [PASS] {label} ({exc})")
    else:
        FAILED += 1
        print(f"  [FAIL] {label} (không ném {exc_type.__name__} như mong đợi)")


def track(dt, name):
    CREATED.append((dt, name))
    return name


def cleanup():
    frappe.set_user("Administrator")
    try:
        if "orig_holiday_list" in globals() and not orig_holiday_list and "company" in globals():
            frappe.db.set_value("Company", company, "default_holiday_list", None)
    except Exception:
        pass
    for dt, name in reversed(CREATED):
        try:
            if not frappe.db.exists(dt, name):
                continue
            docstatus = frappe.db.get_value(dt, name, "docstatus")
            if docstatus == 1:
                if dt == "Student Leave Application":
                    atts = frappe.get_all("Student Attendance", filters={"leave_application": name}, pluck="name")
                    for att in atts:
                        frappe.db.set_value("Student Attendance", att, "docstatus", 0)
                        frappe.delete_doc("Student Attendance", att, ignore_missing=True, force=True)
                    frappe.db.set_value(dt, name, "docstatus", 0)
                elif dt in ("Level Transfer Request", "Instructor Reschedule Request"):
                    frappe.db.set_value(dt, name, "docstatus", 0)
                elif dt == "Fees":
                    frappe.db.set_value(dt, name, "docstatus", 0)
                    frappe.db.sql("DELETE FROM `tabGL Entry` WHERE voucher_type='Fees' AND voucher_no=%s", (name,))
                    frappe.db.sql("DELETE FROM `tabPayment Ledger Entry` WHERE voucher_type='Fees' AND voucher_no=%s", (name,))
                elif dt == "Program Enrollment":
                    frappe.db.set_value(dt, name, "docstatus", 0)
            frappe.delete_doc(dt, name, ignore_missing=True, force=True)
        except Exception as exc:
            print(f"  [warn] cleanup {dt} {name}: {exc}")


def ensure_user(email, first_name, roles):
    if frappe.db.exists("User", email):
        return email
    u = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": r} for r in roles],
        }
    )
    u.insert(ignore_permissions=True)
    return track("User", u.name)


def ensure_program(name):
    if frappe.db.exists("Program", name):
        return name
    p = frappe.get_doc({"doctype": "Program", "program_name": name})
    p.insert(ignore_permissions=True)
    return track("Program", p.name)


def ensure_academic_year(name, start_date, end_date):
    if frappe.db.exists("Academic Year", name):
        return name
    ay = frappe.get_doc(
        {
            "doctype": "Academic Year",
            "academic_year_name": name,
            "year_start_date": start_date,
            "year_end_date": end_date,
        }
    )
    ay.insert(ignore_permissions=True)
    return track("Academic Year", ay.name)


def ensure_course(name, room_type):
    if frappe.db.exists("Course", name):
        return name
    c = frappe.get_doc(
        {
            "doctype": "Course",
            "course_name": name,
            "custom_required_room_type": room_type,
        }
    )
    c.insert(ignore_permissions=True)
    return track("Course", c.name)


def ensure_room(room_name, room_type):
    existing = frappe.db.get_value("Room", {"room_name": room_name}, "name")
    if existing:
        return existing
    r = frappe.get_doc(
        {
            "doctype": "Room",
            "room_name": room_name,
            "custom_room_type": room_type,
            "seating_capacity": 20,
        }
    )
    r.insert(ignore_permissions=True)
    return track("Room", r.name)


def create_instructor(name, email, levels=None):
    existing = frappe.db.get_value("Instructor", {"instructor_name": name}, "name")
    if existing:
        frappe.db.set_value("Instructor", existing, {"custom_email": email, "custom_teaching_levels": levels, "status": "Active"})
        return existing
    ins = frappe.get_doc(
        {
            "doctype": "Instructor",
            "instructor_name": name,
            "custom_email": email,
            "custom_teaching_levels": levels,
            "status": "Active",
        }
    )
    ins.insert(ignore_permissions=True)
    return track("Instructor", ins.name)


def create_student(email, last_name):
    existing = frappe.db.get_value("Student", {"student_email_id": email}, "name")
    if existing:
        return existing
    s = frappe.get_doc(
        {
            "doctype": "Student",
            "first_name": "_TEST_HOOK",
            "last_name": last_name,
            "student_email_id": email,
            "guardians": [],
        }
    )
    s.flags.ignore_mandatory = True
    s.insert(ignore_permissions=True)
    return track("Student", s.name)


try:
    frappe.set_user("Administrator")

    from ling_ielts.ling_room import validate_course_schedule_room
    from ling_ielts.ling_ielts.doctype.instructor_reschedule_request.instructor_reschedule_request import (
        get_reschedule_suggestions,
    )

    now = now_datetime()
    ay_name = ensure_academic_year("_TEST_AY_2026", add_days(today(), -30), add_days(today(), 120))
    prog_low = ensure_program("_TEST_IELTS_4.0_4.5")
    prog_high = ensure_program("_TEST_IELTS_5.0_5.5")
    course_list = ensure_course("_TEST_COURSE_LISTENING", "Phòng Listening")
    room_list = ensure_room("_TEST_ROOM_LISTENING", "Phòng Listening")
    room_speak = ensure_room("_TEST_ROOM_SPEAKING", "Phòng Speaking")

    inst1_user = ensure_user("_test_inst1@example.com", "Inst1", ["Instructor", "Academics User"])
    inst2_user = ensure_user("_test_inst2@example.com", "Inst2", ["Instructor", "Academics User"])
    other_user = ensure_user("_test_mgr@example.com", "Mgr", ["Education Manager", "Academics User", "Instructor"])

    inst1 = create_instructor("_TEST_GV_1", inst1_user, prog_low)
    inst2 = create_instructor("_TEST_GV_2", inst2_user, prog_low)
    student = create_student("_test_hook_stu@example.com", "STU01")

    enr = frappe.get_doc(
        {
            "doctype": "Program Enrollment",
            "student": student,
            "program": prog_low,
            "academic_year": ay_name,
            "enrollment_date": today(),
        }
    )
    enr.insert(ignore_permissions=True)
    enr.submit()
    track("Program Enrollment", enr.name)

    fee_cat = frappe.get_all("Fee Category", pluck="name", limit_page_length=1)[0]
    fee_struct = frappe.get_all("Fee Structure", filters={"docstatus": 1}, pluck="name", limit_page_length=1)[0]
    company = frappe.get_all("Company", pluck="name", limit_page_length=1)[0]

    # Đảm bảo Company có Holiday List để Education StudentLeaveApplication.validate_holiday_list() không lỗi
    orig_holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
    if not orig_holiday_list:
        hl_name = "_TEST_HL_2026"
        if not frappe.db.exists("Holiday List", hl_name):
            hl = frappe.get_doc(
                {
                    "doctype": "Holiday List",
                    "holiday_list_name": hl_name,
                    "from_date": add_days(today(), -60),
                    "to_date": add_days(today(), 365),
                }
            )
            hl.insert(ignore_permissions=True)
            track("Holiday List", hl.name)
        frappe.db.set_value("Company", company, "default_holiday_list", hl_name)

    # 1. TEST FEES HOOK
    print("\n== 1. Fees Discount Hook ==")
    frappe.set_user(other_user)
    fee_ok = frappe.get_doc(
        {
            "doctype": "Fees",
            "student": student,
            "company": company,
            "posting_date": today(),
            "due_date": today(),
            "program_enrollment": enr.name,
            "program": prog_low,
            "fee_structure": fee_struct,
            "custom_discount_amount": 500000,
            "custom_discount_reason": "Học bổng đầu vào",
            "components": [{"fees_category": fee_cat, "amount": 5500000}],
        }
    )
    fee_ok.insert(ignore_permissions=True)
    track("Fees", fee_ok.name)
    check("Fees trừ discount còn 5,000,000", fee_ok.grand_total == 5000000 and fee_ok.outstanding_amount == 5000000)
    check("Fees tự lưu Discount Applied By", fee_ok.custom_discount_applied_by == other_user)

    fee_over = frappe.get_doc(
        {
            "doctype": "Fees",
            "student": student,
            "company": company,
            "posting_date": today(),
            "due_date": today(),
            "program_enrollment": enr.name,
            "program": prog_low,
            "fee_structure": fee_struct,
            "custom_discount_amount": 6000000,
            "components": [{"fees_category": fee_cat, "amount": 5500000}],
        }
    )
    expect_error("Fees chặn giảm vượt học phí (BR-FEE-04)", frappe.ValidationError, lambda: fee_over.insert(ignore_permissions=True), contains="BR-FEE-04")

    frappe.set_user("Administrator")
    # Pay off fee_ok so student can enter Student Group (BR-FEE-03)
    fee_ok.submit()
    frappe.db.set_value("Fees", fee_ok.name, "outstanding_amount", 0)

    # Create Student Groups
    sg_low = frappe.get_doc(
        {
            "doctype": "Student Group",
            "student_group_name": "_TEST_SG_LOW",
            "group_based_on": "Batch",
            "program": prog_low,
            "academic_year": ay_name,
            "instructors": [{"instructor": inst1}],
            "students": [{"student": student, "active": 1}],
        }
    )
    sg_low.insert(ignore_permissions=True)
    track("Student Group", sg_low.name)

    sg_high = frappe.get_doc(
        {
            "doctype": "Student Group",
            "student_group_name": "_TEST_SG_HIGH",
            "group_based_on": "Batch",
            "program": prog_high,
            "academic_year": ay_name,
            "instructors": [{"instructor": inst1}],
        }
    )
    sg_high.insert(ignore_permissions=True)
    track("Student Group", sg_high.name)

    # 2. TEST COURSE SCHEDULE IS ONLINE (ling_room.py)
    print("\n== 2. Course Schedule Is Online (ling_room.py) ==")
    cs_date_future = add_days(today(), 2)
    av_future = frappe.get_doc(
        {
            "doctype": "Instructor Availability",
            "instructor": inst1,
            "program": prog_low,
            "available_date": cs_date_future,
            "from_time": "08:00:00",
            "to_time": "12:00:00",
        }
    )
    av_future.insert(ignore_permissions=True)
    track("Instructor Availability", av_future.name)

    cs_wrong_room = frappe.get_doc(
        {
            "doctype": "Course Schedule",
            "student_group": sg_low.name,
            "instructor": inst1,
            "course": course_list,
            "schedule_date": cs_date_future,
            "from_time": "08:00:00",
            "to_time": "10:00:00",
            "room": room_speak,
            "custom_is_online": 0,
        }
    )
    expect_error("Course Schedule offline sai loại phòng bị chặn (BR-ROOM-02)", frappe.ValidationError, lambda: cs_wrong_room.insert(ignore_permissions=True), contains="BR-ROOM-02")

    cs_online = frappe.get_doc(
        {
            "doctype": "Course Schedule",
            "student_group": sg_low.name,
            "instructor": inst1,
            "course": course_list,
            "schedule_date": cs_date_future,
            "from_time": "08:00:00",
            "to_time": "10:00:00",
            "custom_is_online": 1,
            "custom_online_meeting_link": "https://meet.example.com/test",
        }
    )
    cs_online.insert(ignore_permissions=True)
    track("Course Schedule", cs_online.name)
    check("Course Schedule tick Is Online bỏ qua check phòng và lưu không cần Room", bool(cs_online.name))
    frappe.delete_doc("Course Schedule", cs_online.name, force=True)

    # 3. TEST STUDENT LEAVE APPLICATION
    print("\n== 3. Student Leave Application ==")
    # Late session (in 15 minutes)
    late_dt = now + timedelta(minutes=15)
    if late_dt.date() == (late_dt + timedelta(hours=2)).date():
        av_late = frappe.get_doc(
            {
                "doctype": "Instructor Availability",
                "instructor": inst1,
                "program": prog_low,
                "available_date": late_dt.date(),
                "from_time": late_dt.strftime("%H:%M:%S"),
                "to_time": (late_dt + timedelta(hours=2)).strftime("%H:%M:%S"),
            }
        )
        av_late.insert(ignore_permissions=True)
        track("Instructor Availability", av_late.name)

        cs_late = frappe.get_doc(
            {
                "doctype": "Course Schedule",
                "student_group": sg_low.name,
                "instructor": inst1,
                "course": course_list,
                "schedule_date": late_dt.date(),
                "from_time": late_dt.strftime("%H:%M:%S"),
                "to_time": (late_dt + timedelta(hours=2)).strftime("%H:%M:%S"),
                "room": room_list,
            }
        )
        cs_late.insert(ignore_permissions=True)
        track("Course Schedule", cs_late.name)

        sla_late = frappe.get_doc(
            {
                "doctype": "Student Leave Application",
                "student": student,
                "from_date": late_dt.date(),
                "to_date": late_dt.date(),
                "attendance_based_on": "Course Schedule",
                "course_schedule": cs_late.name,
                "reason": "Xin nghỉ gấp",
            }
        )
        expect_error("Chặn nộp trễ < 30 phút (BR-LEAVE-05)", frappe.ValidationError, lambda: sla_late.insert(ignore_permissions=True), contains="BR-LEAVE-05")

    # Valid session in 2 days
    cs_valid = frappe.get_doc(
        {
            "doctype": "Course Schedule",
            "student_group": sg_low.name,
            "instructor": inst1,
            "course": course_list,
            "schedule_date": cs_date_future,
            "from_time": "08:00:00",
            "to_time": "10:00:00",
            "room": room_list,
        }
    )
    cs_valid.insert(ignore_permissions=True)
    track("Course Schedule", cs_valid.name)

    sla_ok = frappe.get_doc(
        {
            "doctype": "Student Leave Application",
            "student": student,
            "from_date": cs_date_future,
            "to_date": cs_date_future,
            "attendance_based_on": "Course Schedule",
            "course_schedule": cs_valid.name,
            "reason": "Bận việc gia đình",
        }
    )
    sla_ok.insert(ignore_permissions=True)
    track("Student Leave Application", sla_ok.name)
    check("Tự ghi Submitted At khi tạo đơn nghỉ", bool(sla_ok.custom_submitted_at))

    # Non-assigned manager cannot approve (BR-LEAVE-06)
    frappe.set_user(other_user)
    sla_reload = frappe.get_doc("Student Leave Application", sla_ok.name)
    sla_reload.custom_leave_status = "Chấp thuận"
    expect_error("Quản lý không phụ trách lớp bị chặn duyệt (BR-LEAVE-06)", frappe.PermissionError, lambda: sla_reload.save(), contains="BR-LEAVE-06")

    # Assigned instructor approves & submits
    frappe.set_user(inst1_user)
    sla_inst = frappe.get_doc("Student Leave Application", sla_ok.name)
    sla_inst.custom_leave_status = "Chấp thuận"
    sla_inst.save()
    sla_inst.submit()
    check("Giáo viên phụ trách duyệt thành công & ghi Processed By/At", sla_inst.custom_processed_by == inst1_user and bool(sla_inst.custom_processed_at))
    frappe.set_user("Administrator")

    # 4. TEST IELTS PLACEMENT TEST
    print("\n== 4. IELTS Placement Test ==")
    pt_bad_range = frappe.get_doc(
        {
            "doctype": "IELTS Placement Test",
            "candidate_name": "_TEST_CAND_1",
            "test_date": today(),
            "listening": 9.5,
            "reading": 6.0,
            "writing": 6.0,
            "speaking": 6.0,
            "overall_band": 7.0,
        }
    )
    expect_error("Chặn điểm kỹ năng > 9 (AC-02.2)", frappe.ValidationError, lambda: pt_bad_range.insert(ignore_permissions=True), contains="AC-02.2")

    pt_low_band = frappe.get_doc(
        {
            "doctype": "IELTS Placement Test",
            "candidate_name": "_TEST_CAND_2",
            "test_date": today(),
            "listening": 2.0,
            "reading": 2.5,
            "writing": 2.5,
            "speaking": 2.5,
            "overall_band": 2.5,
        }
    )
    expect_error("Chặn band tổng < 3.0 (BR-STU-05)", frappe.ValidationError, lambda: pt_low_band.insert(ignore_permissions=True), contains="BR-STU-05")

    pt_ok = frappe.get_doc(
        {
            "doctype": "IELTS Placement Test",
            "candidate_name": "_TEST_CAND_3",
            "test_date": today(),
            "listening": 6.0,
            "reading": 6.0,
            "writing": 6.0,
            "speaking": 7.0,
            "overall_band": 1.0,
        }
    )
    pt_ok.insert(ignore_permissions=True)
    track("IELTS Placement Test", pt_ok.name)
    check("Tự tính band làm tròn 0.5 chuẩn IELTS (6.25 -> 6.5) (BR-STU-03)", pt_ok.overall_band == 6.5)

    # 5. TEST LEVEL TRANSFER REQUEST
    print("\n== 5. Level Transfer Request ==")
    ltr = frappe.get_doc(
        {
            "doctype": "Level Transfer Request",
            "student": student,
            "current_program": prog_low,
            "current_student_group": sg_low.name,
            "new_program": prog_high,
            "new_student_group": sg_high.name,
            "total_sessions": 24,
            "remaining_sessions": 12,
            "current_fee": 4000000,
            "new_fee": 5500000,
            "status": "Học viên đồng ý",
        }
    )
    ltr.insert(ignore_permissions=True)
    track("Level Transfer Request", ltr.name)
    check("Tính phụ thu 750,000 VNĐ (BR-TR-02)", ltr.additional_fee == 750000)
    ltr.submit()
    ltr.reload()
    if ltr.fees_doc:
        track("Fees", ltr.fees_doc)
    old_members = [r.student for r in frappe.get_doc("Student Group", sg_low.name).students]
    new_members = [r.student for r in frappe.get_doc("Student Group", sg_high.name).students]
    check("on_submit tạo Fees phụ thu 750,000", bool(ltr.fees_doc) and frappe.db.get_value("Fees", ltr.fees_doc, "grand_total") == 750000)
    check("on_submit chuyển học viên sang lớp mới (BR-TR-03)", student not in old_members and student in new_members and ltr.status == "Hoàn tất chuyển lớp")
    new_enr = frappe.db.get_value("Program Enrollment", {"student": student, "program": prog_high, "docstatus": 1}, "name")
    if new_enr:
        track("Program Enrollment", new_enr)

    # 6. TEST INSTRUCTOR RESCHEDULE REQUEST
    print("\n== 6. Instructor Reschedule Request ==")
    # Add availability for inst1 in same week (tomorrow or cs_date_future + 1) and inst2 at cs_valid slot
    alt_week_date = add_days(cs_date_future, 1)
    next_week_date = add_days(cs_date_future, 8)
    for d in (alt_week_date, next_week_date):
        av_alt = frappe.get_doc(
            {
                "doctype": "Instructor Availability",
                "instructor": inst1,
                "program": prog_low,
                "available_date": d,
                "from_time": "10:00:00",
                "to_time": "12:00:00",
            }
        )
        av_alt.insert(ignore_permissions=True)
        track("Instructor Availability", av_alt.name)

    av_inst2 = frappe.get_doc(
        {
            "doctype": "Instructor Availability",
            "instructor": inst2,
            "program": prog_low,
            "available_date": cs_date_future,
            "from_time": "08:00:00",
            "to_time": "10:00:00",
        }
    )
    av_inst2.insert(ignore_permissions=True)
    track("Instructor Availability", av_inst2.name)

    # Check suggestions (BR-TCH-03)
    sugg = get_reschedule_suggestions(course_schedule=cs_valid.name, instructor=inst1)
    check("Gợi ý trả đủ 4 phương án ưu tiên (BR-TCH-03)", len(sugg["priorities"]) == 4)
    check("Phương án 2 có giáo viên thay thế inst2", any(o["instructor"] == inst2 for o in sugg["priorities"][1]["options"]))

    # Check emergency flag when requested_at is < 24h before cs_valid
    irr_emerg = frappe.get_doc(
        {
            "doctype": "Instructor Reschedule Request",
            "instructor": inst1,
            "course_schedule": cs_valid.name,
            "requested_at": get_datetime(f"{cs_date_future} 08:00:00") - timedelta(hours=10),
            "reason": "Nghỉ ốm đột xuất",
            "status": "Chấp thuận",
            "resolution_type": "Lùi lịch",
            "new_schedule_date": alt_week_date,
            "new_from_time": "10:00:00",
            "new_to_time": "12:00:00",
            "new_room": room_list,
        }
    )
    irr_emerg.insert(ignore_permissions=True)
    track("Instructor Reschedule Request", irr_emerg.name)
    check("Tự đánh dấu is_emergency = 1 khi báo nghỉ < 1 ngày (BR-TCH-01)", irr_emerg.is_emergency == 1)

    irr_emerg.submit()
    cs_valid.reload()
    check(
        "Submit 'Lùi lịch' tự cập nhật Course Schedule gốc",
        str(cs_valid.schedule_date) == str(alt_week_date) and cs_valid.custom_session_status == "Đã dời lịch",
    )

    # Check 'Dạy bù online' creates online Course Schedule
    irr_online = frappe.get_doc(
        {
            "doctype": "Instructor Reschedule Request",
            "instructor": inst1,
            "course_schedule": cs_valid.name,
            "requested_at": now,
            "reason": "Xin dạy bù online",
            "status": "Chấp thuận",
            "resolution_type": "Dạy bù online",
            "new_schedule_date": next_week_date,
            "new_from_time": "10:00:00",
            "new_to_time": "12:00:00",
        }
    )
    irr_online.insert(ignore_permissions=True)
    track("Instructor Reschedule Request", irr_online.name)
    irr_online.submit()
    irr_online.reload()
    if irr_online.makeup_course_schedule:
        track("Course Schedule", irr_online.makeup_course_schedule)
    cs_valid.reload()
    makeup_doc = frappe.get_doc("Course Schedule", irr_online.makeup_course_schedule)
    check(
        "Submit 'Dạy bù online' đánh dấu buổi cũ & tạo Course Schedule online mới",
        cs_valid.custom_session_status == "Nghỉ - chờ bù"
        and makeup_doc.custom_is_online == 1
        and makeup_doc.custom_session_status == "Dạy bù",
    )

finally:
    cleanup()
    frappe.db.commit()
    frappe.destroy()

print(f"\nTổng kết kiểm thử Hooks: {PASSED} PASS, {FAILED} FAIL")
sys.exit(1 if FAILED else 0)
