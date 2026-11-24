# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from decimal import Decimal, ROUND_HALF_UP

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


SKILL_FIELDS = ("listening", "reading", "writing", "speaking")


def calculate_ielts_overall_band(listening, reading, writing, speaking):
    """BR-STU-03: Trung bình cộng 4 kỹ năng, làm tròn nửa-lên tới 0.5 gần nhất theo chuẩn IELTS."""
    total = (
        Decimal(str(flt(listening)))
        + Decimal(str(flt(reading)))
        + Decimal(str(flt(writing)))
        + Decimal(str(flt(speaking)))
    )
    average = total / Decimal("4")
    rounded_half = (average * Decimal("2")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / Decimal("2")
    return float(rounded_half)


class IELTSPlacementTest(Document):
    def validate(self):
        # AC-02.2: Đủ 4 kỹ năng và mỗi điểm phải nằm trong thang 0–9
        for field in SKILL_FIELDS:
            raw = getattr(self, field, None)
            if raw is None or raw == "":
                frappe.throw(_("Vui lòng nhập đầy đủ điểm {0} (AC-02.2).").format(field.title()))
            score = flt(raw)
            if score < 0 or score > 9:
                frappe.throw(
                    _("Điểm {0} ({1}) phải nằm trong thang 0–9 (AC-02.2).").format(field.title(), score)
                )

        # BR-STU-03: Tự tính overall_band làm tròn 0.5
        self.overall_band = calculate_ielts_overall_band(
            self.listening,
            self.reading,
            self.writing,
            self.speaking,
        )

        # BR-STU-05: Chỉ tiếp nhận học viên có band tổng từ 3.0 đến 8.0
        if self.overall_band < 3.0 or self.overall_band > 8.0:
            frappe.throw(
                _("Band tổng ({0}) nằm ngoài phạm vi tiếp nhận 3.0–8.0 của trung tâm (BR-STU-05).").format(
                    self.overall_band
                )
            )
