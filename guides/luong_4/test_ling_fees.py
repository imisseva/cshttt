"""Kiểm thử tự động Luồng 4 — Chặn ghi danh khi chưa đóng đủ học phí.

Chạy bên trong container bằng Python của bench, từ thư mục sites:

    docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 \
        /workspace/development/frappe-bench/env/bin/python /tmp/ling-fees/test_ling_fees.py

Yêu cầu trước khi chạy: đã cài `ling_fees.py` (xem README). Script tự tạo học viên
và chứng từ Fees tối thiểu để kiểm thử, rồi dọn dẹp sau khi chạy.
"""
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
            # Fees được đặt docstatus=1 để mô phỏng chứng từ đã Submit; hạ về draft trước khi xoá
            if dt == "Fees":
                frappe.db.set_value(dt, name, "docstatus", 0)
            frappe.delete_doc(dt, name, ignore_missing=True, force=True)
        except Exception as exc:
            print(f"  [warn] dọn dẹp {dt} {name} thất bại: {exc}")


def create_student(email, last_name):
    existing = frappe.db.get_value("Student", {"student_email_id": email}, "name")
    if existing:
        return existing
    student = frappe.get_doc(
        {
            "doctype": "Student",
            "first_name": "_TEST_LING",
            "last_name": last_name,
            "student_email_id": email,
        }
    )
    student.insert(ignore_permissions=True)
    CREATED.append(("Student", student.name))
    return student.name


def create_fees(student, outstanding, program=None):
    fee = frappe.get_doc(
        {
            "doctype": "Fees",
            "student": student,
            "naming_series": "EDU-FEE-.YYYY.-",
            "company": "tri",
            "posting_date": frappe.utils.today(),
            "due_date": frappe.utils.today(),
            "program": program,
        }
    )
    fee.flags.ignore_validate = True
    fee.flags.ignore_mandatory = True
    fee.insert(ignore_permissions=True)
    frappe.db.set_value("Fees", fee.name, "grand_total", outstanding)
    frappe.db.set_value("Fees", fee.name, "outstanding_amount", outstanding)
    frappe.db.set_value("Fees", fee.name, "docstatus", 1)
    CREATED.append(("Fees", fee.name))
    return fee.name


try:
    frappe.set_user("Administrator")

    from education.ling_fees import (
        student_has_full_payment,
        validate_student_group_fees,
        check_group_fees,
    )

    # --- Tạo dữ liệu test ---
    paid_student = create_student("_test_ling_paid01@example.com", "PAID01")
    unpaid_student = create_student("_test_ling_unpaid01@example.com", "UNPAID01")
    print(f"Học viên đã đóng đủ: {paid_student}")
    print(f"Học viên còn nợ: {unpaid_student}")

    create_fees(paid_student, 0)
    create_fees(unpaid_student, 3500000)
    print("Đã tạo chứng từ Fees (paid: outstanding=0, unpaid: outstanding=3.5tr)")

    # --- Test student_has_full_payment ---
    print("\n== student_has_full_payment ==")
    check("Học viên đã đóng đủ -> True", student_has_full_payment(paid_student) is True)
    check("Học viên còn nợ -> False", student_has_full_payment(unpaid_student) is False)
    check("Học viên không tồn tại -> False", student_has_full_payment("_TEST_NOT_EXIST_STUDENT") is False)

    # --- Test validate_student_group_fees ---
    print("\n== validate_student_group_fees ==")

    class MockRow:
        def __init__(self, student):
            self.student = student

    class MockStudentGroup:
        def __init__(self, students, program=None):
            self.students = students
            self.program = program

    check(
        "Lớp chỉ có học viên đã đóng đủ -> OK",
        validate_student_group_fees(MockStudentGroup([MockRow(paid_student)])) is None,
    )
    expect_throw(
        "Lớp có học viên còn nợ -> ném lỗi BR-FEE-03",
        lambda: validate_student_group_fees(MockStudentGroup([MockRow(unpaid_student)])),
    )
    expect_throw(
        "Lớp gồm cả đóng đủ lẫn còn nợ -> ném lỗi",
        lambda: validate_student_group_fees(
            MockStudentGroup([MockRow(paid_student), MockRow(unpaid_student)])
        ),
    )
    check(
        "Lớp chưa có học viên -> OK",
        validate_student_group_fees(MockStudentGroup([])) is None,
    )

    # --- Test check_group_fees ---
    print("\n== check_group_fees ==")
    result = check_group_fees([paid_student, unpaid_student], None)
    by_student = {row["student"]: row for row in result}
    check("Trả đủ 2 học viên", len(result) == 2)
    check(
        "Đánh dấu đúng trạng thái đóng đủ",
        by_student[paid_student]["fully_paid"] is True
        and by_student[paid_student]["outstanding_amount"] == 0,
    )
    check(
        "Đánh dấu đúng trạng thái còn nợ",
        by_student[unpaid_student]["fully_paid"] is False
        and by_student[unpaid_student]["outstanding_amount"] == 3500000,
    )

finally:
    cleanup()
    frappe.db.commit()
    frappe.destroy()

print(f"\nKết quả Luồng 4: {PASSED} PASS, {FAILED} FAIL")
sys.exit(1 if FAILED else 0)
