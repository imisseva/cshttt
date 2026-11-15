"""Fee payment validation for the Ling IELTS enrollment flow.

Luồng 4 - Quản lý học phí & thu tiền:
  - validate_student_group_fees: chặn lưu Student Group khi có học viên chưa
    đóng đủ 100% học phí (BR-FEE-03).
  - check_group_fees: trả trạng thái học phí của danh sách học viên, dùng cho
    nút "Kiểm tra học phí" trên giao diện.
"""
import frappe
from frappe import _


def student_has_full_payment(student, program=None):
    """True khi học viên có ít nhất một chứng từ Fees đã Submit, không còn nợ.

    Nếu lớp có Program, chỉ xét chứng từ thuộc đúng Program đó. Khi lớp chưa có
    Program, chỉ cần một chứng từ bất kỳ đã đóng đủ.
    """
    filters = {"student": student, "docstatus": 1, "outstanding_amount": ["<=", 0]}
    if program:
        return bool(
            frappe.get_all("Fees", filters={**filters, "program": program}, limit_page_length=1)
        )
    return bool(frappe.get_all("Fees", filters=filters, limit_page_length=1))


def validate_student_group_fees(doc, method=None):
    """BR-FEE-03: học viên phải đóng đủ 100% học phí mới được xếp vào lớp."""
    students = [row.student for row in doc.students if getattr(row, "student", None)]
    if not students:
        return

    program = getattr(doc, "program", None)
    unpaid = [student for student in students if not student_has_full_payment(student, program)]

    if unpaid:
        frappe.throw(
            _("Các học viên sau chưa đóng đủ 100% học phí nên không thể xếp vào lớp (BR-FEE-03): {0}.").format(
                ", ".join(unpaid)
            )
        )


@frappe.whitelist()
def check_group_fees(students, program=None):
    """Trả trạng thái học phí của danh sách học viên (dùng cho nút kiểm tra)."""
    if isinstance(students, str):
        students = frappe.parse_json(students)
    students = [student for student in students if student]

    result = []
    for student in students:
        fees = frappe.get_all(
            "Fees",
            filters={"student": student, "docstatus": 1},
            fields=["name", "program", "outstanding_amount"],
            order_by="outstanding_amount asc",
        )
        result.append(
            {
                "student": student,
                "outstanding_amount": min(
                    (row.get("outstanding_amount") or 0 for row in fees), default=None
                ),
                "fully_paid": student_has_full_payment(student, program),
            }
        )
    return result
