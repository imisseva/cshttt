"""Fee payment and discount validation for the Ling IELTS enrollment flow.

Luồng 4 - Quản lý học phí & thu tiền:
  - validate_fees_discount: trừ custom_discount_amount, chặn giảm vượt học phí
    (BR-FEE-04) và tự lưu custom_discount_applied_by.
  - validate_student_group_fees: chặn lưu Student Group khi có học viên chưa
    đóng đủ 100% học phí (BR-FEE-03).
  - check_group_fees: trả trạng thái học phí của danh sách học viên, dùng cho
    nút "Kiểm tra học phí" trên giao diện.
"""
import frappe
from frappe import _
from frappe.utils import flt, money_in_words


def validate_fees_discount(doc, method=None):
    """BR-FEE-02 / BR-FEE-04: Áp dụng giảm giá, chặn vượt tổng phí và lưu người áp dụng."""
    base_total = sum(flt(row.amount) for row in (getattr(doc, "components", None) or []))
    discount = flt(getattr(doc, "custom_discount_amount", 0))

    if discount < 0:
        frappe.throw(_("Mức giảm giá không được nhỏ hơn 0."))

    if discount > base_total:
        frappe.throw(
            _("Mức giảm giá ({0}) không được lớn hơn tổng học phí ({1}) (BR-FEE-04).").format(
                frappe.format_value(discount, {"fieldtype": "Currency"}),
                frappe.format_value(base_total, {"fieldtype": "Currency"}),
            )
        )

    precision = doc.precision("grand_total") if hasattr(doc, "precision") else 2
    net_total = flt(base_total - discount, precision)
    doc.grand_total = net_total
    doc.outstanding_amount = net_total
    doc.grand_total_in_words = money_in_words(net_total)

    if discount > 0:
        if not getattr(doc, "custom_discount_applied_by", None) or (
            hasattr(doc, "has_value_changed") and doc.has_value_changed("custom_discount_amount")
        ):
            doc.custom_discount_applied_by = frappe.session.user
    else:
        doc.custom_discount_applied_by = None


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
    if getattr(getattr(doc, "flags", None), "skip_ling_fee_check", False):
        return

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
