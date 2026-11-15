function ling_set_instructor_query(frm) {
    frm.set_query("instructor", () => ({
        query: "education.ling_scheduling.instructor_query",
        filters: {
            student_group: frm.doc.student_group,
            schedule_date: frm.doc.schedule_date,
            from_time: frm.doc.from_time,
            to_time: frm.doc.to_time,
            current_schedule: frm.is_new() ? "" : frm.doc.name
        }
    }));
}

frappe.ui.form.on("Course Schedule", {
    setup(frm) {
        // The standard Education onload handler also reads this array.
        frm.instructors = frm.instructors || [];
    },
    onload_post_render: ling_set_instructor_query,
    refresh: ling_set_instructor_query,
    student_group: ling_set_instructor_query,
    schedule_date: ling_set_instructor_query,
    from_time: ling_set_instructor_query,
    to_time: ling_set_instructor_query
});
