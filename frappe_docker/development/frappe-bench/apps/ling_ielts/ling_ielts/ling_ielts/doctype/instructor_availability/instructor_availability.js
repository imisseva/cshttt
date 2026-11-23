frappe.ui.form.on("Instructor Availability", {
    validate(frm) {
        const start = frm.doc.from_time;
        const end = frm.doc.to_time;

        if (start && end && start >= end) {
            frappe.throw("Giờ kết thúc phải sau giờ bắt đầu.");
        }
    }
});
