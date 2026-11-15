frappe.ui.form.on("IELTS Placement Test", {
    refresh(frm) {
        frm.add_custom_button("Tính band", () => {
            const fields = [
                "listening",
                "reading",
                "writing",
                "speaking"
            ];

            const scores = fields.map(
                field => Number(frm.doc[field])
            );

            const invalid = scores.some(
                score => !Number.isFinite(score) || score < 0 || score > 9
            );

            if (invalid) {
                frappe.throw("Điểm mỗi kỹ năng phải từ 0 đến 9.");
            }

            const average = scores.reduce(
                (total, score) => total + score, 0
            ) / 4;

            const band = Math.round(average * 2) / 2;

            frm.set_value("overall_band", band);
        });
    }
});
