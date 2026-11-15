// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Level Transfer Request", {
    refresh(frm) {
        // Tự động tính khi mở form
        calculate_additional_fee(frm);
    },

    total_sessions(frm) {
        calculate_additional_fee(frm);
    },

    remaining_sessions(frm) {
        calculate_additional_fee(frm);
    },

    current_fee(frm) {
        calculate_additional_fee(frm);
    },

    new_fee(frm) {
        calculate_additional_fee(frm);
    }
});

function calculate_additional_fee(frm) {
    let total = frm.doc.total_sessions || 24;
    let remaining = frm.doc.remaining_sessions || 0;
    let current_fee = frm.doc.current_fee || 0;
    let new_fee = frm.doc.new_fee || 0;

    if (total > 0 && remaining >= 0) {
        let diff = new_fee - current_fee;
        if (diff > 0) {
            let additional = Math.round((diff * remaining) / total);
            frm.set_value("additional_fee", additional);
        } else {
            frm.set_value("additional_fee", 0);
        }
    }
}
