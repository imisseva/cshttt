function ling_group_instructor_query(frm) {
    frm.set_query("instructor", "instructors", (doc, child_doctype, child_name) => {
        const other_instructors = (doc.instructors || [])
            .filter(row => row.name !== child_name && row.instructor)
            .map(row => row.instructor);

        return other_instructors.length
            ? { filters: { name: ["not in", other_instructors] } }
            : {};
    });
}

frappe.ui.form.on("Student Group", {
    setup: ling_group_instructor_query,
    refresh: ling_group_instructor_query
});

frappe.ui.form.on("Student Group Instructor", {
    instructors_add: ling_group_instructor_query
});
