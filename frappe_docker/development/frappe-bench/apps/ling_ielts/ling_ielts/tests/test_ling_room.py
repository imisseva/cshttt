"""Kiểm thử tự động Luồng 3 — Phân bổ phòng học.

Chạy bên trong container bằng Python của bench, từ thư mục sites:

    docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 \
        /workspace/development/frappe-bench/env/bin/python /tmp/ling-room/test_ling_room.py

Yêu cầu trước khi chạy: đã áp custom field `Room.custom_room_type` và
`Course.custom_required_room_type`, và đã cài `ling_room.py` (xem README).
"""
import json
import os
import sys

import frappe

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


def expect_throw(label, fn):
    global PASSED, FAILED
    try:
        fn()
    except frappe.ValidationError as exc:
        PASSED += 1
        print(f"  [PASS] {label}  ({exc})")
    else:
        FAILED += 1
        print(f"  [FAIL] {label} (không ném lỗi như mong đợi)")


def remove_if_exists(dt, name):
    if name and frappe.db.exists(dt, name):
        frappe.delete_doc(dt, name, ignore_missing=True, force=True)


def cleanup():
    for dt, name in reversed(CREATED):
        try:
            remove_if_exists(dt, name)
        except Exception as exc:
            print(f"  [warn] dọn dẹp {dt} {name} thất bại: {exc}")


try:
    frappe.set_user("Administrator")

    from ling_ielts.ling_room import (
        get_required_room_type,
        validate_course_schedule_room,
        room_query,
    )

    COURSE = "_TEST_LING_COURSE_LISTENING"
    ROOM_LISTENING = "_TEST_LING_ROOM_LISTENING"
    ROOM_SPEAKING = "_TEST_LING_ROOM_SPEAKING"

    # --- Tạo dữ liệu test ---
    remove_if_exists("Course", COURSE)
    course = frappe.get_doc(
        {
            "doctype": "Course",
            "course_name": COURSE,
            "custom_required_room_type": "Phòng Listening",
        }
    )
    course.insert(ignore_permissions=True)
    CREATED.append(("Course", course.name))
    print(f"Đã tạo Course: {course.name}")

    rooms = {}
    for room_name, room_type in ((ROOM_LISTENING, "Phòng Listening"), (ROOM_SPEAKING, "Phòng Speaking")):
        existing = frappe.db.get_value("Room", {"room_name": room_name}, "name")
        if existing:
            frappe.delete_doc("Room", existing, ignore_missing=True, force=True)
        room = frappe.get_doc(
            {
                "doctype": "Room",
                "room_name": room_name,
                "custom_room_type": room_type,
            }
        )
        room.insert(ignore_permissions=True)
        rooms[room_type] = room.name
        CREATED.append(("Room", room.name))
        print(f"Đã tạo Room: {room.name} ({room_type})")

    # --- Test get_required_room_type ---
    print("\n== get_required_room_type ==")
    check("Course có yêu cầu -> trả đúng loại", get_required_room_type(COURSE) == "Phòng Listening")
    check("Course None -> None", get_required_room_type(None) is None)
    check("Course không tồn tại -> None", get_required_room_type("_TEST_NOT_EXIST_COURSE") is None)

    # --- Test validate_course_schedule_room ---
    print("\n== validate_course_schedule_room ==")

    class MockSchedule:
        def __init__(self, course, room):
            self.course = course
            self.room = room

    check(
        "Phòng đúng loại -> OK",
        validate_course_schedule_room(MockSchedule(COURSE, rooms["Phòng Listening"])) is None,
    )
    expect_throw(
        "Phòng sai loại -> ném lỗi BR-ROOM-02",
        lambda: validate_course_schedule_room(MockSchedule(COURSE, rooms["Phòng Speaking"])),
    )
    check(
        "Chưa chọn Course -> bỏ qua",
        validate_course_schedule_room(MockSchedule(None, rooms["Phòng Listening"])) is None,
    )
    check(
        "Chưa chọn Room -> bỏ qua",
        validate_course_schedule_room(MockSchedule(COURSE, None)) is None,
    )

    # --- Test room_query ---
    print("\n== room_query ==")
    try:
        result = room_query("Room", "", "name", 0, 20, json.dumps({"course": COURSE}))
        names = [r[0] for r in result]
        check(
            "room_query chỉ trả phòng đúng loại",
            rooms["Phòng Listening"] in names and rooms["Phòng Speaking"] not in names,
        )
        result_all = room_query("Room", "", "name", 0, 20, json.dumps({}))
        names_all = [r[0] for r in result_all]
        check(
            "Không có course -> trả hết phòng",
            rooms["Phòng Listening"] in names_all and rooms["Phòng Speaking"] in names_all,
        )
    except Exception as exc:
        FAILED += 1
        print(f"  [FAIL] room_query ném lỗi: {exc}")

finally:
    cleanup()
    frappe.db.commit()
    frappe.destroy()

print(f"\nKết quả Luồng 3: {PASSED} PASS, {FAILED} FAIL")
sys.exit(1 if FAILED else 0)

