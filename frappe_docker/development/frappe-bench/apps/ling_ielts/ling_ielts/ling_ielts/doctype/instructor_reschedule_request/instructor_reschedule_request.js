// Copyright (c) 2026, Ling IELTS and contributors
// For license information, please see license.txt

function ling_apply_reschedule_option(frm, option) {
    frm.set_value("status", "Chấp thuận");
    frm.set_value("resolution_type", option.resolution_type);

    if (option.resolution_type === "Đổi giáo viên") {
        frm.set_value("replacement_instructor", option.instructor);
        frm.set_value("new_schedule_date", "");
        frm.set_value("new_from_time", "");
        frm.set_value("new_to_time", "");
        frm.set_value("new_room", "");
    } else {
        frm.set_value("replacement_instructor", "");
        frm.set_value("new_schedule_date", option.schedule_date || "");
        frm.set_value("new_from_time", option.from_time || "");
        frm.set_value("new_to_time", option.to_time || "");
        frm.set_value("new_room", option.room || "");
    }
}

function ling_show_suggestions_dialog(frm, data) {
    const priorities = data.priorities || [];
    let html = `<div style="margin-bottom: 10px;">
        <strong>${__("Đề xuất ưu tiên (BR-TCH-03)")}:</strong>
        <span class="indicator-pill blue">${frappe.utils.escape_html(data.recommended_type || "")}</span>
        <div class="text-muted small" style="margin-top:4px;">
            ${__("Tuần buổi học")}: ${frappe.utils.escape_html(data.week_start)} → ${frappe.utils.escape_html(data.week_end)} |
            ${__("Trong khóa")}: ${frappe.utils.escape_html(data.term_start)} → ${frappe.utils.escape_html(data.term_end)}
        </div>
    </div>`;

    const all_options = [];
    priorities.forEach((tier) => {
        html += `<div style="margin-top: 12px; border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
            <div style="font-weight: 600; margin-bottom: 6px;">${frappe.utils.escape_html(tier.label)}</div>`;
        if (!tier.options || !tier.options.length) {
            html += `<div class="text-muted small">${__("Không có phương án khả dụng.")}</div>`;
        } else {
            html += `<div class="list-group">`;
            tier.options.slice(0, 5).forEach((opt) => {
                const idx = all_options.length;
                all_options.push(opt);
                let desc = "";
                if (opt.resolution_type === "Đổi giáo viên") {
                    desc = `${frappe.utils.escape_html(opt.instructor_name)} (${frappe.utils.escape_html(opt.instructor)})`;
                } else {
                    desc = `${frappe.utils.escape_html(opt.schedule_date)} | ${frappe.utils.escape_html(opt.from_time)} - ${frappe.utils.escape_html(opt.to_time)}`;
                    if (opt.room) {
                        desc += ` | ${__("Phòng")}: ${frappe.utils.escape_html(opt.room_name || opt.room)}`;
                    } else if (opt.resolution_type === "Dạy bù online") {
                        desc += ` | Online`;
                    }
                }
                html += `<div class="list-group-item d-flex justify-content-between align-items-center" style="padding: 6px 10px;">
                    <span>${desc}</span>
                    <button type="button" class="btn btn-xs btn-primary ling-pick-opt" data-idx="${idx}">
                        ${__("Áp dụng")}
                    </button>
                </div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
    });

    const dialog = new frappe.ui.Dialog({
        title: __("Gợi ý 4 phương án xử lý (BR-TCH-03)"),
        size: "large",
        fields: [{ fieldtype: "HTML", fieldname: "suggestions_html" }],
        primary_action_label: __("Đóng"),
        primary_action() {
            dialog.hide();
        }
    });

    dialog.fields_dict.suggestions_html.$wrapper.html(html);
    dialog.fields_dict.suggestions_html.$wrapper.find(".ling-pick-opt").on("click", function () {
        const idx = Number($(this).attr("data-idx"));
        const picked = all_options[idx];
        if (picked) {
            ling_apply_reschedule_option(frm, picked);
            dialog.hide();
        }
    });
    dialog.show();
}

frappe.ui.form.on("Instructor Reschedule Request", {
    refresh(frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Gợi ý phương án (BR-TCH-03)"), () => {
                if (!frm.doc.course_schedule) {
                    frappe.msgprint(__("Vui lòng chọn 'Buổi học cần nghỉ' trước khi xem gợi ý."));
                    return;
                }
                frappe.call({
                    method: "ling_ielts.ling_ielts.doctype.instructor_reschedule_request.instructor_reschedule_request.get_reschedule_suggestions",
                    args: {
                        course_schedule: frm.doc.course_schedule,
                        instructor: frm.doc.instructor,
                        request_name: frm.is_new() ? null : frm.doc.name
                    },
                    callback(r) {
                        if (r.message) {
                            ling_show_suggestions_dialog(frm, r.message);
                        }
                    }
                });
            });
        }
    }
});
