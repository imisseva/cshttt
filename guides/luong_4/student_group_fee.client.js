frappe.ui.form.on("Student Group", {
    refresh(frm) {
        frm.add_custom_button(__("Kiểm tra học phí"), () => {
            const students = (frm.doc.students || [])
                .map(row => row.student)
                .filter(Boolean);

            if (!students.length) {
                frappe.msgprint("Chưa có học viên nào trong lớp.");
                return;
            }

            frappe.call({
                method: "education.ling_fees.check_group_fees",
                args: { students: students, program: frm.doc.program },
                callback(r) {
                    const rows = (r.message || []).map(item => {
                        const outstanding = item.outstanding_amount == null
                            ? "Chưa có phiếu thu"
                            : item.outstanding_amount;
                        return item.student + " - còn nợ " + outstanding + " - " +
                            (item.fully_paid ? "Đã đóng đủ" : "Chưa đóng đủ");
                    });

                    frappe.msgprint({
                        title: __("Kết quả kiểm tra học phí"),
                        message: rows.join("<br>") || "Không có dữ liệu.",
                        indicator: "blue"
                    });
                }
            });
        }).addClass("btn-primary");
    }
});
