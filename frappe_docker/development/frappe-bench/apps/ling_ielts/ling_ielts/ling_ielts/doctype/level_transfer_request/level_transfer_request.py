# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class LevelTransferRequest(Document):
    def validate(self):
        # 1. Kiểm tra số buổi
        if not self.total_sessions or self.total_sessions <= 0:
            self.total_sessions = 24

        if self.remaining_sessions < 0 or self.remaining_sessions > self.total_sessions:
            frappe.throw(
                _("Số buổi còn lại ({0}) không hợp lệ (phải từ 0 đến {1}).").format(
                    self.remaining_sessions, self.total_sessions
                )
            )

        # 2. Quy tắc BR-TR-08: Chỉ hỗ trợ chuyển lên cấp cao hơn
        if flt(self.new_fee) < flt(self.current_fee):
            frappe.throw(
                _("Chỉ hỗ trợ chuyển lên cấp độ cao hơn (Học phí cấp mới phải lớn hơn hoặc bằng cấp cũ) (BR-TR-08).")
            )

        # 3. Tính phụ thu tự động theo công thức BR-TR-02
        diff = flt(self.new_fee) - flt(self.current_fee)
        if diff > 0 and self.remaining_sessions > 0:
            self.additional_fee = round((diff * self.remaining_sessions) / self.total_sessions)
        else:
            self.additional_fee = 0

    def before_submit(self):
        if self.status == "Học viên từ chối":
            frappe.throw(
                _("Không thể Submit đề xuất khi học viên đã từ chối chuyển cấp (BR-TR-04).")
            )
        if self.status not in ("Học viên đồng ý", "Đã thanh toán phụ thu", "Hoàn tất chuyển lớp"):
            frappe.throw(
                _("Vui lòng cập nhật Trạng thái thành 'Học viên đồng ý' hoặc 'Đã thanh toán phụ thu' trước khi Submit.")
            )
        if self.current_student_group and self.new_student_group and self.current_student_group == self.new_student_group:
            frappe.throw(_("Lớp mới dự kiến phải khác lớp hiện tại."))
        if self.new_student_group and self.new_program:
            group_program = frappe.db.get_value("Student Group", self.new_student_group, "program")
            if group_program and group_program != self.new_program:
                frappe.throw(
                    _("Lớp mới {0} đang thuộc Program '{1}', không khớp với cấp độ mới '{2}'.").format(
                        self.new_student_group, group_program, self.new_program
                    )
                )

    def on_submit(self):
        # BR-TR-03: Tạo phiếu Fees phụ thu (nếu additional_fee > 0) và chuyển học viên sang lớp mới
        if flt(self.additional_fee) > 0 and not self.fees_doc:
            fee_name = self._create_additional_fee_doc()
            self.db_set("fees_doc", fee_name)

        self._transfer_student_groups()
        self.db_set("status", "Hoàn tất chuyển lớp")

    def on_cancel(self):
        if self.fees_doc and frappe.db.exists("Fees", self.fees_doc):
            fee = frappe.get_doc("Fees", self.fees_doc)
            if fee.docstatus == 1 and flt(fee.outstanding_amount) == flt(fee.grand_total):
                fee.flags.ignore_permissions = True
                fee.cancel()

        self._revert_student_groups()

    def _get_company(self):
        company = (
            frappe.defaults.get_defaults().get("company")
            or frappe.db.get_single_value("Global Defaults", "default_company")
        )
        if not company:
            companies = frappe.get_all("Company", pluck="name", limit_page_length=1)
            company = companies[0] if companies else None
        if not company:
            frappe.throw(_("Chưa cấu hình Company mặc định trong hệ thống để tạo phiếu Fees."))
        return company

    def _get_academic_context(self):
        academic_year = None
        academic_term = None
        for group_name in (self.new_student_group, self.current_student_group):
            if group_name and frappe.db.exists("Student Group", group_name):
                grp = frappe.db.get_value(
                    "Student Group", group_name, ["academic_year", "academic_term"], as_dict=True
                )
                if grp:
                    academic_year = academic_year or grp.academic_year
                    academic_term = academic_term or grp.academic_term

        if not academic_year:
            enrollments = frappe.get_all(
                "Program Enrollment",
                filters={"student": self.student, "docstatus": 1},
                fields=["academic_year", "academic_term"],
                order_by="creation desc",
                limit_page_length=1,
            )
            if enrollments:
                academic_year = enrollments[0].academic_year
                academic_term = academic_term or enrollments[0].academic_term

        if not academic_year:
            years = frappe.get_all("Academic Year", pluck="name", order_by="creation desc", limit_page_length=1)
            academic_year = years[0] if years else None

        return academic_year, academic_term

    def _get_or_create_program_enrollment(self, academic_year, academic_term):
        existing = frappe.get_all(
            "Program Enrollment",
            filters={"student": self.student, "program": self.new_program, "docstatus": 1},
            pluck="name",
            order_by="creation desc",
            limit_page_length=1,
        )
        if existing:
            return existing[0]

        if not academic_year:
            any_enr = frappe.get_all(
                "Program Enrollment",
                filters={"student": self.student, "docstatus": 1},
                pluck="name",
                order_by="creation desc",
                limit_page_length=1,
            )
            if any_enr:
                return any_enr[0]
            frappe.throw(_("Không tìm thấy Academic Year để tạo Program Enrollment cho học viên."))

        enrollment = frappe.get_doc(
            {
                "doctype": "Program Enrollment",
                "student": self.student,
                "program": self.new_program,
                "academic_year": academic_year,
                "academic_term": academic_term,
                "enrollment_date": today(),
            }
        )
        enrollment.insert(ignore_permissions=True)
        enrollment.submit()
        return enrollment.name

    def _get_fee_category(self):
        if frappe.db.exists("Fee Category", "Phụ thu chuyển cấp"):
            return "Phụ thu chuyển cấp"
        if frappe.db.exists("Fee Category", "Học phí"):
            return "Học phí"
        categories = frappe.get_all("Fee Category", pluck="name", limit_page_length=1)
        if categories:
            return categories[0]
        cat = frappe.get_doc({"doctype": "Fee Category", "category_name": "Phụ thu chuyển cấp"})
        cat.insert(ignore_permissions=True)
        return cat.name

    def _get_fee_structure(self):
        for filters in (
            {"program": self.new_program, "docstatus": 1},
            {"program": self.current_program, "docstatus": 1},
            {"docstatus": 1},
        ):
            structures = frappe.get_all("Fee Structure", filters=filters, pluck="name", limit_page_length=1)
            if structures:
                return structures[0]
        return None

    def _create_additional_fee_doc(self):
        company = self._get_company()
        academic_year, academic_term = self._get_academic_context()
        program_enrollment = self._get_or_create_program_enrollment(academic_year, academic_term)
        fee_category = self._get_fee_category()
        fee_structure = self._get_fee_structure()

        fee = frappe.get_doc(
            {
                "doctype": "Fees",
                "student": self.student,
                "company": company,
                "posting_date": today(),
                "due_date": today(),
                "program_enrollment": program_enrollment,
                "program": self.new_program,
                "academic_year": academic_year,
                "academic_term": academic_term,
                "fee_structure": fee_structure,
                "components": [
                    {
                        "fees_category": fee_category,
                        "amount": flt(self.additional_fee),
                        "description": _("Phụ thu chuyển cấp từ {0} sang {1} ({2})").format(
                            self.current_program, self.new_program, self.name
                        ),
                    }
                ],
            }
        )
        if not fee_structure:
            fee.flags.ignore_mandatory = True
        fee.insert(ignore_permissions=True)
        fee.submit()
        return fee.name

    def _transfer_student_groups(self):
        if self.current_student_group and frappe.db.exists("Student Group", self.current_student_group):
            old_group = frappe.get_doc("Student Group", self.current_student_group)
            kept_rows = [row for row in old_group.students if row.student != self.student]
            if len(kept_rows) != len(old_group.students):
                old_group.students = kept_rows
                for idx, row in enumerate(old_group.students, start=1):
                    row.idx = idx
                old_group.flags.skip_ling_fee_check = True
                old_group.save(ignore_permissions=True)

        if self.new_student_group and frappe.db.exists("Student Group", self.new_student_group):
            new_group = frappe.get_doc("Student Group", self.new_student_group)
            existing_students = {row.student for row in new_group.students if row.student}
            if self.student not in existing_students:
                new_group.append(
                    "students",
                    {
                        "student": self.student,
                        "student_name": self.student_name
                        or frappe.db.get_value("Student", self.student, "student_name"),
                        "active": 1,
                    },
                )
                new_group.flags.skip_ling_fee_check = True
                new_group.save(ignore_permissions=True)

    def _revert_student_groups(self):
        if self.new_student_group and frappe.db.exists("Student Group", self.new_student_group):
            new_group = frappe.get_doc("Student Group", self.new_student_group)
            kept_rows = [row for row in new_group.students if row.student != self.student]
            if len(kept_rows) != len(new_group.students):
                new_group.students = kept_rows
                for idx, row in enumerate(new_group.students, start=1):
                    row.idx = idx
                new_group.flags.skip_ling_fee_check = True
                new_group.save(ignore_permissions=True)

        if self.current_student_group and frappe.db.exists("Student Group", self.current_student_group):
            old_group = frappe.get_doc("Student Group", self.current_student_group)
            existing_students = {row.student for row in old_group.students if row.student}
            if self.student not in existing_students:
                old_group.append(
                    "students",
                    {
                        "student": self.student,
                        "student_name": self.student_name
                        or frappe.db.get_value("Student", self.student, "student_name"),
                        "active": 1,
                    },
                )
                old_group.flags.skip_ling_fee_check = True
                old_group.save(ignore_permissions=True)
