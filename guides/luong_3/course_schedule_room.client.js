function ling_set_room_query(frm) {
    frm.set_query("room", () => ({
        query: "education.ling_room.room_query",
        filters: {
            course: frm.doc.course
        }
    }));
}

frappe.ui.form.on("Course Schedule", {
    onload_post_render: ling_set_room_query,
    refresh: ling_set_room_query,
    course: ling_set_room_query
});
