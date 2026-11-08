# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class LevelTransferRequest(Document):
    def validate(self):
        # 1. Kiểm tra số buổi
        if not self.total_sessions or self.total_sessions <= 0:
            self.total_sessions = 24

        if self.remaining_sessions < 0 or self.remaining_sessions > self.total_sessions:
            frappe.throw(_("Số buổi còn lại ({0}) không hợp lệ (phải từ 0 đến {1}).").format(
                self.remaining_sessions, self.total_sessions
            ))

        # 2. Quy tắc BR-TR-08: Chỉ hỗ trợ chuyển lên cấp cao hơn
        if self.new_fee < self.current_fee:
            frappe.throw(_("Chỉ hỗ trợ chuyển lên cấp độ cao hơn (Học phí cấp mới phải lớn hơn hoặc bằng cấp cũ)."))

        # 3. Tính phụ thu tự động theo công thức BR-TR-02
        diff = (self.new_fee or 0) - (self.current_fee or 0)
        if diff > 0 and self.remaining_sessions > 0:
            self.additional_fee = round((diff * self.remaining_sessions) / self.total_sessions)
        else:
            self.additional_fee = 0
