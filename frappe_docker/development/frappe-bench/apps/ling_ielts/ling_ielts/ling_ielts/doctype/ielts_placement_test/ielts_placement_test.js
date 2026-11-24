function ling_compute_placement_band(frm) {
    const fields = ["listening", "reading", "writing", "speaking"];
    const values = fields.map((field) => frm.doc[field]);

    if (values.some((v) => v === null || v === undefined || v === "")) {
        return null;
    }

    const scores = values.map((v) => Number(v));
    if (scores.some((score) => !Number.isFinite(score) || score < 0 || score > 9)) {
        return null;
    }

    const average = scores.reduce((total, score) => total + score, 0) / 4;
    return Math.round(average * 2) / 2;
}

frappe.ui.form.on("IELTS Placement Test", {
    refresh(frm) {
        frm.add_custom_button(__("Tính band"), () => {
            const band = ling_compute_placement_band(frm);
            if (band === null) {
                frappe.throw(__("Vui lòng nhập đủ 4 kỹ năng trong thang điểm 0–9."));
            }
            frm.set_value("overall_band", band);
        });
    },

    listening(frm) {
        const band = ling_compute_placement_band(frm);
        if (band !== null) frm.set_value("overall_band", band);
    },

    reading(frm) {
        const band = ling_compute_placement_band(frm);
        if (band !== null) frm.set_value("overall_band", band);
    },

    writing(frm) {
        const band = ling_compute_placement_band(frm);
        if (band !== null) frm.set_value("overall_band", band);
    },

    speaking(frm) {
        const band = ling_compute_placement_band(frm);
        if (band !== null) frm.set_value("overall_band", band);
    },

    validate(frm) {
        const band = ling_compute_placement_band(frm);
        if (band !== null) {
            frm.set_value("overall_band", band);
        }
    }
});
