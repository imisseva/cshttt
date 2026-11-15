"""Build an evidence-linked, reproducible requirements mapping from the audit."""
import json
import re
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'analysis'
inventory = json.loads((out/'basecode/inventory.json').read_text(encoding='utf-8'))
requirements = (root/'extracted_doc.txt').read_text(encoding='utf-8').splitlines()

# Scores measure source-level functional fit, not deployment completion or UAT.
# 1 = main required behavior already implemented; .5 = partial support; 0 = absent.
rows = [
 (1,1,'Must',.5,.5,'Hồ sơ học viên','Student, Guardian, Student Guardian','Có hồ sơ và liên kết phụ huynh; chưa bắt buộc ngày sinh, ít nhất một phụ huynh/liên hệ và chống trùng người thực theo BR-STU-01/02.','E01'),
 (2,1,'Must',.5,.5,'Test đầu vào 4 kỹ năng','Assessment Plan/Result, Assessment Criteria','Có nền đánh giá; chưa có test đầu vào độc lập trước xếp lớp, kiểm tra đủ 4 kỹ năng 0–9, tính band và gán cấp IELTS.','E02'),
 (3,1,'Should',.5,.5,'Lịch sử cấp độ qua các khóa','Program Enrollment, Course Enrollment','Có lịch sử ghi danh nhiều kỳ; chưa có lịch sử cấp IELTS chuẩn hóa, ngày hiệu lực và liên kết quyết định chuyển cấp.','E03'),
 (4,2,'Must',.5,.5,'Chặn trùng giờ giáo viên','Course Schedule.validate_overlap','Đã có bộ chặn; phép so sánh bỏ sót trường hợp cùng giờ bắt đầu, lịch mới ngắn hơn. Cần sửa và kiểm thử biên.','E04'),
 (5,2,'Should',.5,.5,'Lịch linh động giáo viên','Instructor, Course Schedule, Course Scheduling Tool','Nhập lịch tùy khung giờ được; chưa có nơi giáo viên đăng ký khả dụng và ràng buộc lịch nằm trong khung đã đăng ký.','E04'),
 (6,2,'Should',.5,.5,'Thông báo lịch xác nhận','Notification/Notification Log của Frappe','Có cơ chế thông báo để cấu hình; chưa có quy tắc xác nhận lịch và người nhận đúng buổi của Ling IELTS.','F01'),
 (7,2,'Should',0,0,'Gợi ý giáo viên thay / online','Instructor, Course Schedule','Chưa có thuật toán xếp theo cấp độ + khả dụng, phương án online và thứ tự lựa chọn.','E04'),
 (8,3,'Must',0,.5,'Gợi ý phòng đúng loại còn trống','Room + custom_room_type, Course Schedule','Bản gốc chỉ có phòng/sức chứa; dự án đã thêm loại phòng. Chưa có lọc loại + khung giờ và chặn loại không phù hợp.','P02'),
 (9,3,'Must',.5,.5,'Chặn trùng phòng','Course Schedule, education.education.utils','Có bộ chặn chung với lịch giáo viên; cùng lỗi biên khoảng thời gian ở US-04.','E04'),
 (10,4,'Must',1,1,'Giảm giá và tính học phí','Fee Structure, Fee Schedule, Sales Invoice','Có giảm giá %, số tiền trên hóa đơn, kiểm tra giảm không vượt tổng tiền; bảng giá IELTS/VND cần cấu hình.','E05/E06'),
 (11,4,'Must',.5,.5,'Đóng đủ mới được vào lớp','Sales Invoice, Payment Entry, Program Enrollment, Student Group','Có số còn phải thu và trạng thái Paid; chưa có chặn ghi danh/xếp lớp phía server khi chưa thanh toán đủ.','E03/E06'),
 (12,5,'Must',1,1,'Nhập kết quả kiểm tra tuần','Assessment Plan, Assessment Result, Assessment Group','Có nhập điểm, ngày kiểm tra, lớp/học viên, chặn học viên ngoài nhóm, điểm tối đa và trùng kết quả. Cần cấu hình kỳ tuần/tháng và vai trò.','E02'),
 (13,5,'Must',0,.5,'Tự tính phụ thu chuyển cấp','Level Transfer Request.validate','Dự án tính đúng hai ví dụ AC-13; học phí/số buổi còn nhập tay, chưa lấy từ bảng giá/lịch và điều kiện vượt cấp.','P01'),
 (14,5,'Should',0,.5,'Lịch sử đề xuất và từ chối','Level Transfer Request, track_changes','Có chứng từ riêng, trạng thái và theo dõi sửa đổi; chưa có thao tác quyết định của chính học viên, người/thời điểm duyệt và toàn bộ chuỗi quyết định.','P01'),
 (15,5,'Should',0,0,'Học viên đồng ý hoặc từ chối chuyển cấp','Student Portal + Level Transfer Request','Chưa có trang/API nhận quyết định; quyền Student chưa được khai báo trên DocType chuyển cấp.','P01/E09'),
 (16,5,'Should',0,.5,'Giáo viên chủ động đề xuất giữa kỳ','Level Transfer Request.proposed_by/transfer_reason','Instructor được tạo đề xuất; chưa giới hạn đúng lớp phụ trách, liên kết bằng chứng điểm và luồng quản lý duyệt.','P01'),
 (17,5,'Should',1,1,'Học viên xem điểm/chuyên cần','Student Portal: Grades.vue, Attendance.vue','Đã có trang điểm, chuyên cần và API kiểm tra học viên/phụ huynh. Cần cấp tài khoản và dữ liệu học tập.','E09'),
 (18,6,'Must',0,0,'Giáo viên xin nghỉ dạy','Chưa có Instructor Leave Request','Student Leave Application dùng cho học viên; chưa có chứng từ nghỉ dạy và cờ nghỉ đột xuất.','P03'),
 (19,6,'Must',0,0,'Quản lý duyệt nghỉ dạy','Workflow của Frappe là nền tảng','Chưa có Workflow/transition và nghiệp vụ duyệt nghỉ dạy trên site.','P03'),
 (20,6,'Must',0,0,'Ưu tiên lùi lịch → thay → bù → online','Course Schedule là dữ liệu tái sử dụng','Chưa có dịch vụ gợi ý, xác nhận và cập nhật lịch theo thứ tự bắt buộc.','P03'),
 (21,6,'Should',0,0,'Theo dõi số buổi đã dạy/còn nợ','Course Schedule, Student Group','Chưa có trạng thái đã diễn ra/hủy/bù và đối soát số buổi gốc, tránh đếm trùng khi lùi lịch.','P03'),
 (22,7,'Must',.5,.5,'Học viên xin nghỉ đúng buổi','Student Leave Application, portal apply_leave','Có đơn và portal; chọn theo ngày, API lấy buổi đầu trong khoảng. Chưa có chọn đúng buổi thuộc lớp, hạn 30 phút và lý do bắt buộc.','E07/E09'),
 (23,7,'Must',.5,.5,'Giáo viên phụ trách duyệt xin nghỉ','Student Leave Application, DocPerm','Instructor có submit, nhưng chưa có ba trạng thái duyệt và kiểm tra người duyệt chính là giáo viên của buổi; quản lý chỉ xem chưa được thiết lập.','E07'),
 (24,7,'Must',.5,.5,'Điểm danh đúng lớp/buổi/giáo viên','Student Attendance Tool, Student Attendance','Có danh sách lớp, chặn học viên ngoài lớp và trùng bản ghi; chưa ràng buộc người điểm danh là giáo viên được phân công và buổi đã diễn ra.','E08'),
 (25,7,'Must',.5,.5,'Có mặt / Vắng có phép / Vắng không phép','Student Attendance.status = Present/Absent/Leave','Đủ ba giá trị và liên kết đơn; chưa bảo đảm cả lớp đủ trạng thái, không ghi đè Leave khi điểm danh hàng loạt, và áp dụng đúng từng buổi.','E07/E08'),
 (26,7,'Should',.5,.5,'Quản lý chỉ xem đơn nghỉ và chuyên cần','Attendance reports, Student Leave Application','Có báo cáo/danh sách; còn thiếu cấu hình chỉ đọc đúng vai trò và phạm vi từng lớp.','E07/E08'),
 (27,7,'Should',1,1,'Phụ huynh xem kết quả con','Guardian, Student Guardian, portal Guardian mode','Bản đang cài đã có chế độ phụ huynh, chọn con và kiểm tra liên kết; không cần tự xây cổng phụ huynh từ đầu. Việc kích hoạt vẫn cần trung tâm chốt.','E09'),
]
mapping = [dict(zip(('id','flow','priority','base','current','requirement','objects','gap','evidence'), row)) for row in rows]
flow_names = {1:'Hồ sơ học viên và đầu vào',2:'Xếp lịch giảng dạy',3:'Phân bổ phòng học',4:'Thu học phí',5:'Đánh giá và chuyển cấp',6:'Giáo viên nghỉ dạy / xử lý lịch',7:'Học viên xin nghỉ và điểm danh'}
totals = {key: sum(r[key] for r in mapping) for key in ('base','current')}
must = [r for r in mapping if r['priority']=='Must']
metrics = {'method':'Equal-weight fit score over 27 stories: 1=implemented main behavior, .5=partial, 0=absent; not a UAT/completion metric.',
           'stories':len(mapping),'base_points':totals['base'],'current_points':totals['current'],
           'base_percent':100*totals['base']/len(mapping),'current_percent':100*totals['current']/len(mapping),
           'must_stories':len(must),'must_current_percent':100*sum(r['current'] for r in must)/len(must),
           'current_status_counts':dict(Counter(str(r['current']) for r in mapping))}
(out/'mapping.json').write_text(json.dumps({'metrics':metrics,'stories':mapping},ensure_ascii=False,indent=2),encoding='utf-8')

module_notes = {
'Accounts':('Kế toán, hóa đơn, thanh toán','Trực tiếp: học phí, công nợ, Sales Invoice/Payment Entry'),
'CRM':('Khách hàng tiềm năng, cơ hội, chiến dịch','Có thể dùng tư vấn tuyển sinh; chưa bắt buộc trong 7 luồng'),
'Buying':('Mua hàng, nhà cung cấp','Ngoài phạm vi A1'),
'Projects':('Dự án, công việc, chấm thời gian','Có thể quản lý việc nội bộ; không dùng thay lớp học'),
'Selling':('Khách hàng, chào giá, đơn bán','Tái sử dụng Customer, cấu hình bán/giảm giá; luồng học phí chính ở Accounts + Education'),
'Setup':('Công ty, kỳ nghỉ, cấu hình tổ chức','Dữ liệu nền cho kế toán và lịch nghỉ'),
'Manufacturing':('Sản xuất, định mức, lệnh sản xuất','Ngoài phạm vi A1'),
'Stock':('Kho, vật tư, luân chuyển tồn kho','Ngoài phạm vi; Item có thể dùng làm mã khoản thu'),
'Support':('Yêu cầu hỗ trợ, xử lý sự cố','Ngoài phạm vi A1'),
'Utilities':('Tiện ích nghiệp vụ dùng chung','Hỗ trợ kỹ thuật, không phải một luồng IELTS'),
'Assets':('Tài sản cố định','Tùy chọn quản lý thiết bị phòng học; ngoài Must'),
'Portal':('Chức năng portal phía ERPNext','Không đồng nhất với cổng học viên của Education'),
'Maintenance':('Lịch và tác vụ bảo trì','Ngoài phạm vi A1'),
'Regional':('Thiết lập nghiệp vụ theo khu vực','Không coi là bộ đáp ứng pháp lý/kế toán Việt Nam đã được kiểm định'),
'ERPNext Integrations':('Tích hợp của ERPNext','Không có tích hợp Zalo sẵn cho yêu cầu này'),
'Quality Management':('Mục tiêu, quy trình và đánh giá chất lượng','Không thay thế Assessment Result học viên'),
'Communication':('Đối tượng phục vụ giao tiếp của ERPNext','Không đồng nghĩa đã cấu hình thông báo 7 luồng'),
'Telephony':('Nhật ký và tích hợp điện thoại','Ngoài phạm vi A1'),
'Bulk Transaction':('Thao tác chứng từ hàng loạt','Tiện ích, không phải nghiệp vụ lớp học'),
'Subcontracting':('Gia công thuê ngoài','Ngoài phạm vi A1'),
'EDI':('Trao đổi dữ liệu điện tử','Ngoài phạm vi A1'),
}

def module_table():
    app=inventory['apps']['erpnext']; counts=Counter(d['module'] for d in app['doctypes'])
    parts=['| # | Module kỹ thuật ERPNext | DocType* | Chức năng | Ánh xạ Ling IELTS |','|---|---|---:|---|---|']
    for i,name in enumerate(app['modules'],1):
        purpose, note=module_notes[name]
        parts.append(f'| {i} | {name} | {counts[name]} | {purpose} | {note} |')
    return '\n'.join(parts)

def flow_table():
    parts=['| Luồng / module nghiệp vụ dự án | User Story | Bản gốc | Hiện tại |','|---|---|---:|---:|']
    for flow in range(1,8):
        group=[r for r in mapping if r['flow']==flow]
        ids=', '.join(f"US-{r['id']:02}" for r in group)
        parts.append(f"| L{flow}. {flow_names[flow]} | {ids} | {100*sum(r['base'] for r in group)/len(group):.1f}% | {100*sum(r['current'] for r in group)/len(group):.1f}% |")
    return '\n'.join(parts)

evidence = {
'E01':('Hồ sơ, phụ huynh','basecode/source/education/education/education/doctype/student/student.json','guardians'),
'E02':('Đánh giá: kiểm tra nhóm/điểm tối đa/trùng','basecode/source/education/education/education/doctype/assessment_result/assessment_result.py','def validate'),
'E03':('Ghi danh: submit tạo khoản thu, chưa có cổng chặn đã trả đủ','basecode/source/education/education/education/doctype/program_enrollment/program_enrollment.py','def on_submit'),
'E04':('Kiểm tra lịch chồng lấn','basecode/source/education/education/education/utils.py','def get_overlap_for'),
'E05':('Giảm giá học phí %','basecode/source/education/education/education/doctype/fee_structure/fee_structure.py','def calculate_total'),
'E06':('Giảm giá không vượt tổng tiền','basecode/source/erpnext/erpnext/controllers-taxes_and_totals.py','discount amount cannot exceed'),
'E07':('Xin nghỉ học và cập nhật điểm danh','basecode/source/education/education/education/doctype/student_leave_application/student_leave_application.py','def update_attendance'),
'E08':('Điểm danh theo lớp/buổi, chống trùng','basecode/source/education/education/education/doctype/student_attendance/student_attendance.py','def validate'),
'E09':('API portal học viên/phụ huynh và xin nghỉ','basecode/source/education/education/education/api.py','def apply_leave'),
'P01':('Controller chuyển cấp do dự án viết','../custom_doctypes/level_transfer_request/level_transfer_request.py','def validate'),
'P02':('Loại phòng đã tùy biến','../custom_doctypes/custom/room.json','custom_room_type'),
'P03':('Kiểm kê site: không có Workflow/DocType nghỉ dạy','basecode/inventory.json','"workflows"'),
'F01':('Danh mục DocType nền tảng, gồm Notification','basecode/inventory.json','"Notification"'),
'F02':('Vòng đời Document phía server','basecode/source/frappe/frappe/model/document.py','def run_before_save_methods'),
}

def evidence_table():
    parts=['| Mã | Bằng chứng đã đọc | Tệp |','|---|---|---|']
    for key,(label,path,needle) in evidence.items():
        resolved=out/path
        lines=resolved.read_text(encoding='utf-8').splitlines()
        line=next((i+1 for i,t in enumerate(lines) if needle in t),1)
        parts.append(f'| {key} | {label} | [{resolved.name}]({path}#L{line}) — dòng {line} |')
    return '\n'.join(parts)

story_table=['| US | Luồng | Ưu tiên | Yêu cầu | Bản gốc | Hiện tại | Đối tượng tái sử dụng | Phần thiếu / căn cứ |','|---|---:|---|---|---:|---:|---|---|']
for r in mapping:
    story_table.append(f"| US-{r['id']:02} | {r['flow']} | {r['priority']} | {r['requirement']} | {100*r['base']:.0f}% | {100*r['current']:.0f}% | {r['objects']} | {r['gap']} [{r['evidence']}] |")

report = '''# Ling IELTS — đối chiếu nghiệp vụ với ERPNext/Frappe Education

Ngày kiểm tra: **08/11/2026**, múi giờ Asia/Bangkok. Tài liệu yêu cầu thực tế là `extracted_doc.txt` (1.082 dòng), tên người dùng gọi là `extracteddoc.txt`.

## Kết quả chính và phạm vi kiểm tra

**Nên tái sử dụng ERPNext + Education cho dữ liệu học viên, lớp, lịch, đánh giá, học phí, điểm danh và portal; tập trung phát triển các quy tắc IELTS và các chuỗi phê duyệt còn thiếu.** Không cần xây lại một hệ thống quản lý trường học từ đầu.

Đã đọc toàn bộ yêu cầu A1, metadata module/DocType của bản đang chạy, controller/API liên quan 7 luồng, các tùy biến của dự án và cấu hình Workflow/Client Script/Server Script trên site. Đây là khảo sát mã nguồn và độ phù hợp chức năng; không phải tuyên bố đã duyệt mọi dòng mã ERPNext hoặc nghiệm thu đầy đủ 7 luồng bằng người dùng thực.

Tệp làm việc:

- [Tài liệu yêu cầu](../extracted_doc.txt).
- [Kiểm kê đầy đủ module và toàn bộ tên DocType](MODULE-INVENTORY.md).
- [Dữ liệu kiểm kê máy đọc được](basecode/inventory.json).
- [Ma trận 27 User Story và cách tính điểm](mapping.json).
- [Kiểm chứng riêng logic controller](checks.json).

''' + f'''| Thành phần | Phiên bản đang cài | Git commit mã gốc | Module kỹ thuật | DocType trong nguồn* |
|---|---|---|---:|---:|
| Frappe Framework | 16.55.2 | `{inventory['apps']['frappe']['sha']}` | 15 | 301 |
| ERPNext | 16.54.0 | `{inventory['apps']['erpnext']['sha']}` | 21 | 534 |
| Frappe Education | 16.0.1 | `{inventory['apps']['education']['sha']}` | 1 | 76 |

''' + '''*Đếm file định nghĩa DocType, gồm bảng con, Single và công cụ. 76 DocType dưới Education gồm **74 định nghĩa gốc + 2 DocType dự án** (`Level Transfer Request`, `doct`); không có nghĩa là 76 module nghiệp vụ. Tổng metadata site là 911 DocType, khớp 301 + 534 + 76. Mã build sinh ra asset thay đổi cục bộ; SHA ghi nhận nền mã gốc, không đại diện cho các tùy biến thêm vào.

Không gộp **Frappe Framework**, **ERPNext** và **Frappe Education** thành một app. Bản này không cài HRMS/Frappe HR; không thể coi module nghỉ phép nhân sự/payroll là đã có chỉ vì giao diện có tên Instructor hoặc liên kết Employee. Payroll và thanh toán online cũng nằm ngoài phạm vi A1.

## Bước 1 — nắm nền tảng và liệt kê đầy đủ module hiện tại

### 1.1. Các module kỹ thuật ERPNext

Nguồn chuẩn cho danh sách là [modules.txt của ERPNext đang chạy](basecode/source/erpnext/erpnext/modules.txt), thay vì danh mục tính năng quảng cáo hoặc tên Workspace trên giao diện.

''' + module_table() + '''

### 1.2. Các module của Frappe Framework

15 module kỹ thuật: **Core, Website, Workflow, Email, Custom, Geo, Desk, Integrations, Printing, Contacts, Automation, System, Build, Data, Users**. Chúng cung cấp tài khoản, quyền, metadata, form/list/report, workflow, thông báo, in ấn, API và nền tảng tùy biến. Có nền tảng Workflow không đồng nghĩa site đã có quy trình duyệt nghiệp vụ: kiểm kê hiện tại có **0 Workflow, 0 Client Script, 0 Server Script**. Controller Python/JS trong app vẫn tồn tại và không nằm trong ba số đếm này.

### 1.3. Education: các nhóm chức năng có sẵn

Education chỉ khai báo **một Module Def là Education**. Để phân tích chức năng có thể chia thành:

| Nhóm chức năng Education | DocType/thành phần chính | Dùng cho Ling IELTS |
|---|---|---|
| Hồ sơ và tuyển sinh | Student, Guardian, Student Applicant, Student Admission | Hồ sơ tập trung, phụ huynh, tiếp nhận |
| Chương trình và ghi danh | Program, Course, Academic Year, Academic Term, Program Enrollment, Course Enrollment | Program biểu diễn cấp/band; Course biểu diễn kỹ năng/môn; ghi danh theo kỳ |
| Lớp và giáo viên | Student Group, Student Batch Name, Instructor | Lớp học, khóa/batch, người dạy |
| Lịch và phòng | Course Schedule, Course Scheduling Tool, Room | Ngày/giờ/phòng/giáo viên, tạo lịch lặp và kiểm tra xung đột |
| Đánh giá | Assessment Group, Assessment Plan, Assessment Criteria, Assessment Result, Grading Scale | Bài kiểm tra tuần/tháng, điểm theo tiêu chí |
| Học phí | Fee Category, Fee Structure, Fee Schedule, Fees; liên kết Sales Invoice/Payment Entry | Bảng phí, hóa đơn và thanh toán |
| Điểm danh và nghỉ học | Student Attendance, Student Attendance Tool, Student Leave Application | Chuyên cần, đơn nghỉ của học viên |
| Nội dung học | Topic, Article, Question, Quiz và các bảng liên quan | Có nền nội dung/quiz; không thuộc trọng tâm 7 luồng A1 |
| Portal và báo cáo | Portal học viên/phụ huynh, 9 report Education | Xem lịch, phí, điểm, chuyên cần và gửi đơn nghỉ |

Danh sách tất cả 76 tên DocType, loại bảng cha/bảng con/Single và toàn bộ 9 tên report được giữ ở phụ lục MODULE-INVENTORY.md; các nhóm trên không phải những module mã nguồn mới.

### 1.4. Module nghiệp vụ của dự án và mã tùy biến hiện có

Theo tài liệu A1, hệ thống có **7 module nghiệp vụ**: (M1) hồ sơ/test đầu vào; (M2) lịch giảng dạy; (M3) phòng học; (M4) học phí; (M5) đánh giá/chuyển cấp; (M6) nghỉ dạy/xử lý lịch; (M7) xin nghỉ/điểm danh. Portal, phân quyền, thông báo và báo cáo là chức năng dùng chung. Hiện chưa có 7 Module Def tương ứng hoặc app `ling_ielts` độc lập.

| Thành phần dự án thực sự đã có | Đánh giá |
|---|---|
| Level Transfer Request | Có trường học viên/lớp/cấp cũ-mới, số buổi, phí, trạng thái, lý do; có controller tính phụ thu và JS hiển thị lại. Chưa có chuỗi phê duyệt/thanh toán/chuyển lớp hoàn chỉnh. |
| Room.custom_room_type | Đã có ba loại phòng giảng dạy/Speaking/Listening; chỉ thêm trường, chưa triển khai thuật toán gợi ý phòng. |
| doct | DocType thử với một Section Break; controller `pass`. Không tính là module nghiệp vụ đã hoàn thành. |
| Student.custom_1 | Có trong metadata site, chưa tìm thấy ý nghĩa nghiệp vụ trong A1 hoặc bản export của repo; không tính điểm đáp ứng. |
| push.ps1 / pull.ps1 / sync_custom.ps1 | Công cụ đồng bộ file và migrate; không tạo thêm logic nghiệp vụ. Phải đọc đúng dữ liệu trong volume Docker. |

Các Custom Field gắn Sales Invoice/Sales Order với Student/Fee Schedule là tích hợp do Education cài đặt; không được tính nhầm là toàn bộ phần tùy biến do nhóm tự viết.

## Bước 2 — quy trình nghiệp vụ và quy trình tin học hóa

Quy trình nghiệp vụ mô tả ai quyết định và xử lý thực tế. Quy trình tin học hóa xác định dữ liệu, màn hình, kiểm tra tự động, sự kiện server và kết quả lưu được. AS-IS chung của A1 là Excel + sổ tay + Zalo; TO-BE phải có dữ liệu tập trung và quy tắc thực thi tại server.

| Module | Quy trình nghiệp vụ TO-BE | Quy trình tin học hóa và điểm kiểm soát |
|---|---|---|
| M1. Hồ sơ / đầu vào | Quản lý tiếp nhận → học viên test → giáo viên chấm → xác định cấp → tạo hồ sơ → thu phí → xếp lớp | Student Applicant/Student + Guardian → **IELTS Placement Test cần bổ sung** → đủ L/S/R/W, 0–9 → tính band theo quy tắc đã chốt → chọn Program phù hợp → Enrollment ở trạng thái chờ đủ điều kiện; giữ lịch sử. |
| M2. Lịch | Quản lý mở lớp theo khóa → phân công giáo viên → kiểm tra giờ → xác nhận → thông báo | Academic Term + Student Group → Course Scheduling Tool tạo từng Course Schedule → kiểm tra trùng + khả dụng/cấp giáo viên → lưu và phát Notification; chưa có bộ gợi ý thay thế/online. |
| M3. Phòng | Xác định loại buổi → tìm phòng đúng loại trống → gán phòng; không có phòng thì báo | Room.custom_room_type + Course/loại buổi → truy vấn loại + khoảng giờ → kiểm tra lại phía server khi lưu Course Schedule → chặn nhầm loại/trùng lịch. Phần lọc loại còn thiếu. |
| M4. Học phí | Tra bảng giá → quản lý giảm giá → lập hóa đơn → nhận đủ tiền → xác nhận tham gia lớp | Fee Structure/Fee Schedule + Sales Invoice → Payment Entry phân bổ đúng hóa đơn → tính outstanding_amount → **server chặn thêm vào Student Group khi chưa đủ tiền**. Không chặn việc tạo bản ghi tiếp nhận/chờ học vì còn cần hồ sơ để lập hóa đơn. |
| M5. Đánh giá / chuyển cấp | Giáo viên nhập điểm → xác định vượt cấp hoặc đề xuất giữa kỳ → quản lý duyệt → báo phụ thu → học viên đồng ý/từ chối → thu đủ phụ thu → chuyển lớp, lưu lịch sử | Assessment Plan/Result → dịch vụ xét 4 tuần → Level Transfer Request + Workflow + portal quyết định → hóa đơn phụ thu + Payment Entry → cập nhật Enrollment/Student Group có giao dịch chống chuyển trùng. Từ chối giữ nguyên lớp. |
| M6. Nghỉ dạy / xử lý lịch | Giáo viên gửi đơn → quản lý duyệt → ưu tiên lùi lịch trong tuần → giáo viên thay cùng cấp → buổi bù trong khóa → online → theo dõi đủ buổi | **Instructor Leave Request cần xây** → Workflow → dịch vụ xử lý lịch → Course Schedule với liên kết lịch gốc/buổi thay/bù và trạng thái → Notification → báo cáo đã dạy/còn nợ. Online chỉ là phương thức, vẫn phải kiểm tra khả dụng giáo viên. |
| M7. Nghỉ học / điểm danh | Học viên gửi đúng buổi trước ≥30 phút → giáo viên phụ trách duyệt → sau buổi học giáo viên ghi 1/3 trạng thái → quản lý xem | Mở rộng Student Leave Application + Workflow ba trạng thái → xác thực học viên thuộc buổi và deadline theo giờ → Student Attendance liên kết đúng course_schedule → Present/Leave/Absent → tổng hợp chuyên cần; không phát sinh buổi bù riêng cho học viên vắng. |

### Luồng xuyên suốt được đề xuất

```mermaid
flowchart TD
    A[Tiếp nhận và test 4 kỹ năng] --> B{Band hợp lệ?}
    B -->|Có| C[Hồ sơ và xác định cấp]
    B -->|Không| X[Xử lý theo quy định đã chốt]
    C --> D[Hóa đơn học phí sau giảm]
    D --> E{Đã thanh toán đủ?}
    E -->|Chưa| F[Chờ thanh toán, chưa xếp lớp]
    E -->|Đủ| G[Ghi danh có hiệu lực và xếp lớp]
    G --> H[Lịch, giáo viên, phòng hợp lệ]
    H --> I[Học, điểm danh, đánh giá]
    I --> J{Đề xuất chuyển cấp?}
    J -->|Có| K[Quản lý duyệt, học viên quyết định]
    K -->|Đồng ý| L[Thu đủ phụ thu]
    L --> M[Chuyển lớp và lưu lịch sử]
    K -->|Từ chối| N[Giữ lớp và lưu quyết định]
```

### Những quy trình chuẩn của ERPNext có thể tái sử dụng

1. **Ghi danh học tập:** Student → Program Enrollment.submit → tạo Course Enrollment và có thể tạo hóa đơn theo Fee Schedule. Mã hiện tại tạo khoản thu khi submit ghi danh, không có kiểm tra đã trả đủ trước khi xếp lớp. Vì vậy cần thiết kế giai đoạn chờ và chặn **kích hoạt lớp**, tránh vòng lặp “phải trả trước khi có hóa đơn”.
2. **Kế toán khoản thu:** bảng phí/khoản thu → Sales Invoice đã submit → Payment Entry đã submit và phân bổ → số còn phải thu/trạng thái Paid. Đây là chứng từ kế toán; không coi một trường status trên đề xuất là bằng chứng đã thanh toán.
3. **Lập lịch:** tạo Course Schedule → validate ngày/giờ/kỳ học → validate_overlap với lớp/giáo viên/phòng và Assessment Plan → lưu. Course Scheduling Tool tạo hàng loạt theo ngày trong tuần; không phải bộ tối ưu phân công giáo viên.
4. **Đánh giá:** Assessment Plan + Criteria → Assessment Result → validate học viên thuộc nhóm, điểm tối đa/trùng → lưu/submit → portal và báo cáo đọc kết quả. IELTS band là một quy tắc riêng còn phải bổ sung.
5. **Nghỉ học chuẩn:** tạo Student Leave Application → submit → update_attendance; cancel → cancel_attendance. `docstatus` chuẩn không biểu diễn riêng “bị từ chối”; cần Workflow/status nghiệp vụ.

## Bước 3 — đọc basecode và chuẩn DocType / quy tắc mã nguồn

### 3.1. Đường đi của mã nguồn

```text
Frappe: metadata + Document + quyền + API + Workflow + migrate
  ├─ ERPNext: Accounts/Selling/Setup/... → chứng từ và nghiệp vụ kế toán
  └─ Education: Student/Enrollment/Schedule/Assessment/Attendance/Fees/Portal
       └─ Ling IELTS hiện tại: DocType chuyển cấp + loại phòng + doct thử nghiệm
```

| Điểm đọc | Hành vi thực tế và ý nghĩa |
|---|---|
| frappe/model/document.py | Chạy quyền, kiểm tra bắt buộc/link/select, controller hooks, ghi dữ liệu, on_update/on_submit, theo dõi phiên bản. Chứng minh phải kiểm tra nghiệp vụ phía server. |
| frappe/permissions.py + DocPerm trong JSON | Quyền theo vai trò là lớp nền; yêu cầu “đúng giáo viên của đúng buổi”, “đúng học viên/con của phụ huynh” cần điều kiện bản ghi/API tương ứng. |
| CourseSchedule.validate và education.education.utils | Kiểm tra kỳ/ngày/giờ, trùng lịch lớp/giáo viên/phòng. Có một trường hợp biên sai, ghi ở phần 4.4. |
| ProgramEnrollment.on_submit; StudentGroup.validate | Tạo ghi danh/khoản thu, kiểm tra trùng và sĩ số. Không có cổng đủ tiền trước khi vào lớp. |
| FeeStructure, FeeSchedule; ERPNext taxes_and_totals | Tính giảm giá %, tạo Sales Invoice/Sales Order, kiểm tra số tiền giảm và theo dõi tổng còn phải thu. |
| AssessmentResult.validate | Kiểm tra học viên thuộc lớp, điểm không vượt tối đa, tính grade tổng và chặn trùng. Không bắt buộc 4 kỹ năng IELTS hay làm tròn band. |
| StudentAttendance / StudentLeaveApplication | Chống trùng bản ghi, liên kết lớp/buổi, cập nhật Leave khi submit đơn; còn thiếu giới hạn người thao tác và deadline. |
| education.education.api + frontend/src | Có portal học viên/phụ huynh, lịch, điểm, phí, chuyên cần; API xin nghỉ theo khoảng ngày chưa đáp ứng lựa chọn chính xác từng buổi. |
| LevelTransferRequest.validate + JS | Có công thức phụ thu trên số nhập, kiểm tra khoảng số buổi và phí mới không thấp hơn. Không có hook chuyển lớp/thu tiền/duyệt. |

Danh mục liên kết bằng chứng cuối báo cáo trỏ đến bản chụp mã đã đọc. Việc rà soát tập trung các controller liên quan 7 luồng; danh mục module/DocType bao phủ toàn bộ metadata của ba app, không suy ra rằng toàn bộ 911 controller đã được review.

### 3.2. Chuẩn một DocType Frappe

| Thành phần | Chuẩn cần nắm | Áp dụng cho dự án |
|---|---|---|
| App / Module / DocType | App là gói cài; Module Def nhóm mã; DocType là mô hình tài liệu + metadata form/quyền. Workspace là giao diện truy cập, không phải định nghĩa module. | Bảy luồng không tự sinh bảy Module Def. Nên gom nghiệp vụ đặc thù vào app riêng khi phát triển tiếp. |
| Tên và thư mục | Thư mục snake_case; Python controller thường CamelCase kế thừa Document; JSON.name phải khớp tên DocType. | `Level Transfer Request` → `level_transfer_request/level_transfer_request.{json,py,js}` → `LevelTransferRequest`. |
| JSON | Khai báo module, field_order, fields, fieldtype/options, reqd, permissions, autoname/naming series, is_submittable, track_changes. | Link đến Student/Program/Student Group; số tiền dùng Currency, số buổi dùng Int; enum trạng thái cần quy tắc chuyển trạng thái. |
| Bảng thường | Thường có bảng `tab<Tên DocType>` và các trường hệ thống name/owner/creation/modified/docstatus. | Chứng từ có danh tính riêng; không dùng tên học viên làm khóa duy nhất thay cho mã Student. |
| Child Table | `istable=1`, liên kết bằng trường Table/options; mang parent, parenttype, parentfield, idx. | Bốn dòng kỹ năng test, khung giờ khả dụng giáo viên; kiểm tra tính đủ/không trùng tại cha. |
| Single | `issingle=1`, cấu hình một bộ giá trị, lưu theo cơ chế Singles; không phải mỗi cấu hình một chứng từ thường. | Có thể dùng Ling IELTS Settings cho deadline/tham số đã được trung tâm chốt. |
| Link / Select | Link là tham chiếu DocType; Select chỉ giới hạn tập giá trị. Trường read_only ở form không đủ để chứng minh giá trị tài chính đáng tin cậy. | `status='Đã thanh toán'` không thay cho đọc Payment Entry/Invoice; phải tính lại phía server. |
| Lifecycle | Với lưu: before_validate → validate → before_save → ghi DB → on_update. Với submit: before_validate → validate → before_submit → ghi DB → on_update/on_submit. Hủy có before_cancel/on_cancel. | Tính phí, kiểm tra điều kiện và quyền ở validate/before_submit; tác động chuyển lớp/đối soát phải có xử lý nguyên tử và tránh thực hiện lặp. |
| docstatus | 0 Draft, 1 Submitted, 2 Cancelled; chỉ dùng submit/cancel khi DocType được cấu hình phù hợp. | Độc lập với trạng thái nghiệp vụ Chờ duyệt/Chấp thuận/Từ chối; không dùng Cancelled để gộp mọi trường hợp từ chối. |
| Workflow | Điều kiện chuyển trạng thái + vai trò + trạng thái chứng từ; Select không tự có máy trạng thái. | Nghỉ dạy, nghỉ học, chuyển cấp cần cấu hình/chức năng phê duyệt thật. |
| JS / Python | JS `frappe.ui.form.on` phục vụ UI, lọc chọn, hiển thị; Python phải thực thi quy tắc dù gọi REST/import. | Công thức và kiểm tra ở JS cần được xác nhận lại trên server; không chỉ lọc giáo viên/học viên bằng trình duyệt. |
| Quyền | DocPerm/Role Permission, User Permission, has_permission, permission_query_conditions và kiểm tra quyền tại API. | Quản lý chỉ xem đơn nghỉ học; giáo viên chỉ duyệt/điểm danh buổi của mình; học viên chỉ thao tác bản thân; phụ huynh đúng con được liên kết. |
| Migration | Metadata/schema được đồng bộ bằng bench --site ... migrate; patch xử lý thay đổi dữ liệu; backup trước thay đổi. | Export customizations/fixtures có chọn lọc; không coi copy file là đã cập nhật DB thành công. |

Theo [tài liệu Controllers](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers), logic nghiệp vụ được đặt trong controller và các lifecycle hook. [Tài liệu Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks#extend-doctype-class) có `extend_doctype_class` từ v16 để mở rộng hành vi; [Database migrations](https://docs.frappe.io/framework/user/en/database-migrations) mô tả việc đồng bộ metadata và patch.

### 3.3. Quy tắc phát triển nên áp dụng

1. Viết phần đặc thù trong **custom app** (ví dụ `ling_ielts`) phụ thuộc ERPNext/Education. Dùng Custom Field/Property Setter/fixtures cho cấu hình, hooks/doc_events/mixin khi mở rộng. Hạn chế sửa trực tiếp controller gốc vì khó nâng cấp và dễ ghi đè.
2. Dùng ORM/Query Builder hoặc SQL có tham số; không ghép đầu vào người dùng vào truy vấn. `@frappe.whitelist()` chỉ cho phép gọi API, không thay thế kiểm tra quyền và phạm vi bản ghi.
3. Các điều kiện đủ tiền, đúng lớp, đúng người duyệt, hạn 30 phút, bốn kỹ năng và band phải ở server. Không dùng `ignore_permissions=True` để tránh thiết kế quyền.
4. Bảng phí/cấp độ là dữ liệu cấu hình có hiệu lực theo khóa; server đọc mức phí liên quan. Không tin học phí nhập tay hoặc mặc định 24 buổi cho mọi kỳ ba tháng.
5. Lưu lịch sử thay đổi và chứng từ nguồn. Chuyển lớp và cập nhật điều kiện thanh toán phải tránh xử lý hai lần; xử lý race khi nhiều người cùng xếp một giáo viên/phòng cần kiểm tra giao dịch và khóa phù hợp.
6. Kiểm thử theo AC trong A1 bằng cả UI và API, bao gồm người dùng sai vai trò, đồng thời, biên giờ, không đủ điểm, giảm quá tiền và tiền chưa phân bổ. Hai file test custom hiện tại chỉ có `pass`, chưa chứng minh nghiệp vụ đã đạt.
7. Script push/pull cần nhận diện dữ liệu Docker volume, kiểm tra exit code và đồng bộ mọi tùy biến cần thiết. Hiện script có thể in thành công dù git push/migrate thất bại; mirror file trên Windows có thể cũ. Đây là điểm cần cải thiện công cụ, không cộng điểm nghiệp vụ.

Mô hình thư mục đề xuất cho giai đoạn sau (chưa tạo/cài app này):

```text
apps/ling_ielts/
  ling_ielts/hooks.py
  ling_ielts/modules.txt
  ling_ielts/ling_ielts/doctype/ielts_placement_test/
  ling_ielts/ling_ielts/doctype/instructor_leave_request/
  ling_ielts/ling_ielts/doctype/instructor_availability/
  ling_ielts/services/enrollment.py
  ling_ielts/services/level_transfer.py
  ling_ielts/services/rescheduling.py
  ling_ielts/permissions.py
  ling_ielts/patches.txt
```

## Bước 4 — ánh xạ, chấm mức đáp ứng và xác định phần tự xây

### 4.1. Phương pháp tính phần trăm

Mẫu số là **27 User Story** trong mục 5.2 A1. Mỗi story có trọng số bằng nhau:

- **100% / 1 điểm:** có sẵn hành vi chính mà story yêu cầu; vẫn cần cấu hình và UAT bằng dữ liệu thật.
- **50% / 0,5 điểm:** có dữ liệu/công cụ hoặc một phần hành vi nhưng còn thiếu ít nhất một quy tắc/AC trọng yếu.
- **0% / 0 điểm:** chưa có hành vi yêu cầu; chỉ có hạ tầng Document/Workflow chung không được tính là đã có nghiệp vụ đó.

“Bản gốc” = ERPNext + Education ở các commit nêu trên, không có code Ling IELTS. “Hiện tại” = bản gốc cộng code và cấu hình tùy biến đã quan sát. Điểm là đánh giá kỹ thuật do người phân tích gán theo ma trận; **không phải số đo chính thức của nhà cung cấp, không phải % mã nguồn tái sử dụng, % tiến độ dự án hoặc % AC đã nghiệm thu**. Nâng mức 50% lên 100% chỉ sau khi xử lý khoảng trống và kiểm thử, không chỉ vì đã thêm trường.

''' + f'''- Bản gốc: **{totals['base']:g}/27 = {metrics['base_percent']:.1f}%** độ phù hợp theo thang trên.
- Hiện tại: **{totals['current']:g}/27 = {metrics['current_percent']:.1f}%**.
- Riêng {len(must)} story Must: **{sum(r['current'] for r in must):g}/{len(must)} = {metrics['must_current_percent']:.1f}%**.
- Hiện tại có **4 story ở mức 100%, 17 story ở mức 50%, 6 story ở mức 0%**. Đây không phải kết quả chạy toàn bộ test chấp nhận.

''' + flow_table() + '''

Tổng là trung bình có trọng số theo số story trong từng luồng, không lấy trung bình đơn giản của 7 phần trăm. Story Should vẫn có trong mẫu số 27; Zalo Could và các mục Won't (online payment/payroll/app di động) không được thêm vào để làm thay đổi tỷ lệ. Các điểm [CẦN CHỐT] được ghi rõ, không tự biến thành quy định đã xác nhận.

### 4.2. Ma trận đầy đủ 27 User Story

''' + '\n'.join(story_table) + '''

### 4.3. Đối chiếu đủ 38 Business Rule

Ký hiệu: **S** = có cơ chế đáp ứng chủ yếu, cần cấu hình; **P** = có một phần; **N** = chưa có quy tắc nghiệp vụ; **C** = trung tâm chưa chốt. Ma trận này bổ sung độ chi tiết; tỷ lệ ở trên vẫn tính theo User Story, không trộn mẫu số 38.

| Business Rule | Mức hiện tại | Có sẵn / cần bổ sung |
|---|---|---|
| BR-STU-01 | P | Student lưu lâu dài; cần chống trùng người thực và hợp nhất lịch sử test/cấp độ. |
| BR-STU-02 | N/C | Có Guardian nhưng chưa bắt buộc ≥1 người giám hộ; điều kiện dưới 18 tuổi cần xác nhận. |
| BR-STU-03 | P | Có nền Assessment; thiếu đủ 4 kỹ năng, 0–9, làm tròn 0,5 và chặn xếp lớp khi thiếu điểm. |
| BR-STU-04 | P | Có Enrollment theo kỳ và chứng từ chuyển cấp; cần lịch sử cấp độ có hiệu lực và không ghi đè. |
| BR-STU-05 | N/C | Chưa có dải band nhận học viên; cần chốt 8,5/9,0 và dưới 3,0. |
| BR-FEE-01 | S | Giảm % ở Fee Structure/khoản thu và giảm tiền trên Sales Invoice; cấp quyền quản lý. |
| BR-FEE-02 | S | Tính tổng sau giảm có sẵn; cấu hình đúng năm mức học phí của A1 và đơn vị VND. |
| BR-FEE-03 | N | Không có chặn Student Group/kích hoạt học khi chưa trả đủ; outstanding sẵn có là đầu vào. |
| BR-FEE-04 | S | Fee Structure chặn % >100; ERPNext chặn discount_amount vượt tổng tiền. |
| BR-TR-01 | P | Có chỗ giáo viên đề xuất giữa kỳ; thiếu xét tự động đủ chuỗi tuần/tháng và duyệt quản lý. |
| BR-TR-02 | P | Controller tính đúng công thức từ số nhập; thiếu nguồn phí và số buổi đáng tin cậy. |
| BR-TR-03 | P | Có Link lớp/cấp mới; chưa tự chuyển Enrollment/Student Group và liên kết khoản thu. |
| BR-TR-04 | P | Có trạng thái từ chối + track_changes; thiếu thao tác học viên và nhật ký quyết định đầy đủ. |
| BR-TR-05 | N/C | Chưa xét mọi bài tuần + bài cuối tháng trong 4 tuần; định nghĩa ngưỡng cần chốt. |
| BR-TR-06 | N | Chưa đếm buổi chưa diễn ra, kể cả bù; hiện remaining_sessions nhập tay. |
| BR-TR-07 | N | Chưa chặn chuyển lớp khi chưa trả đủ phụ thu. |
| BR-TR-08 | P/C | Mới chặn phí mới thấp hơn; không so sánh thứ bậc Program/band. Phí bằng nhau vẫn được chấp nhận. |
| BR-SCH-01 | P | Có chặn chồng lấn; lỗi cùng giờ bắt đầu cần xử lý. |
| BR-SCH-02 | N | Chưa gợi ý giáo viên cùng cấp/rảnh, fallback online; online không làm giáo viên tự hết trùng giờ. |
| BR-ROOM-01 | P | Có chặn chồng lấn; cùng lỗi biên của helper kiểm tra lịch. |
| BR-TCH-01 | N | Thiếu đơn nghỉ giáo viên, thời hạn một ngày và cờ đột xuất. |
| BR-TCH-02 | N/C | Chưa có duyệt nghỉ giáo viên; quyền quản lý cần xác nhận. |
| BR-TCH-03 | N | Chưa có dịch vụ lùi lịch → thay → bù → online có thứ tự. |
| BR-TCH-04 | N | Chưa có số buổi cam kết/đã dạy/còn nợ, kiểm tra đủ trước kết thúc khóa. |
| BR-ATT-01 | P/C | Có điểm danh theo buổi/nhóm; thiếu giới hạn giáo viên phụ trách và buổi đã diễn ra. |
| BR-ATT-02 | P | Có đủ 3 giá trị Present/Absent/Leave; thiếu ràng buộc cả lớp đầy đủ và bảo toàn Leave. |
| BR-ATT-03 | S/C | Điểm danh chỉ ghi nhận, không tự tạo dạy bù cho học viên vắng; cần giữ nguyên quy tắc này khi xây xử lý buổi bù của lớp. |
| BR-ATT-04 | S/C | Dữ liệu tập trung, Link học viên/nhóm/buổi, report/portal có sẵn; cấu hình dùng Course Schedule làm chuẩn. |
| BR-LEAVE-01 | P/C | Có đơn/portal; cần cho chọn đúng buổi và bắt buộc lý do. |
| BR-LEAVE-02 | P/C | Có owner/creation/modified và submit; thiếu 3 trạng thái cùng người/thời điểm xử lý rõ ràng. |
| BR-LEAVE-03 | P/C | Submit đơn ghi Leave, nhưng xử lý theo ngày cần chỉnh để không tác động nhầm buổi. |
| BR-LEAVE-04 | P/C | Có Present/Absent; cần đồng bộ với quyết định duyệt/từ chối đúng buổi. |
| BR-LEAVE-05 | N/C | Chưa kiểm tra ít nhất 30 phút; API cần dùng giờ Course Schedule, không chỉ ngày. |
| BR-LEAVE-06 | P/C | Có vai trò Instructor; chưa kiểm tra giáo viên của đúng buổi, quản lý chỉ đọc. |
| BR-LEAVE-07 | C | Chưa chốt cách xử lý chưa phản hồi trước giờ học; không tự mặc định duyệt hay từ chối. |
| BR-ENR-01 | C | Chưa chốt hoàn tiền/bảo lưu; kế toán có cơ chế riêng nhưng không tự suy ra chính sách trung tâm. |
| BR-ENR-02 | C | Chưa chốt nhận giữa khóa và giá tương ứng. |
| BR-ENR-03 | P/C | Student Group.max_strength kiểm tra sĩ số tối đa; tối thiểu/hủy/gộp và ngưỡng cụ thể chưa chốt. |

### 4.4. Các phát hiện mã nguồn ảnh hưởng kết luận

**A. Chồng lấn lịch có sẵn nhưng chưa hoàn toàn đúng.** Helper `get_overlap_for` được cả giáo viên và phòng sử dụng. Thử riêng biểu thức của hàm trên dữ liệu giả: lịch cũ **18:00–20:00**, lịch mới **18:00–19:00**, cùng ngày/tài nguyên, kết quả phát hiện là **False**, trong khi phải là **True**. Điều kiện bao quát nên được kiểm tra theo `existing_start < new_end AND new_start < existing_end`, kèm ngày/tài nguyên/trạng thái, và trường hợp giáp ranh không chồng lấn. Đây là kết quả chạy hàm đã chụp qua bộ Query Builder trong bộ nhớ, **chưa phải kiểm thử tạo lịch thật trên DB**. Vì vậy US-04/09 chỉ được 50% trong ma trận.

**B. Có ba trạng thái điểm danh, nhưng bulk API chưa bảo toàn nghiệp vụ vắng có phép.** `Student Attendance.status` có Present/Absent/Leave; `mark_attendance` nhận danh sách present/absent, còn submit đơn nghỉ gọi update_attendance. Cần kiểm tra không ghi đè Leave, đúng từng Course Schedule, mọi học viên có trạng thái và giáo viên có quyền đúng buổi. `StudentAttendance.validate` đang không gọi validate_date (dòng bị comment), nên cũng chưa bảo đảm chỉ điểm danh buổi đã diễn ra.

**C. Đơn nghỉ chuẩn thiên về khoảng ngày.** Portal `apply_leave` truy vấn lịch trong from_date/to_date rồi chọn phần tử đầu; không có điều kiện 30 phút. `update_attendance` tìm bản ghi theo student + date, chưa dùng course_schedule trong khóa tìm bản ghi đã có. Với hai buổi cùng ngày cần kiểm thử và sửa để tránh tác động sai buổi. Vai trò Instructor có quyền submit theo DocPerm không tự xác nhận đó là giáo viên phụ trách.

**D. Đề xuất chuyển cấp hiện tại mới là bộ khung + công thức.** Hai ví dụ AC-13 đã kiểm tra trên hàm validate thật ở chế độ độc lập: **12/24 buổi → 750.000đ**, **6/24 buổi → 375.000đ**; cũng chặn số buổi âm/quá tổng và phí mới thấp hơn. Chưa lấy phí từ cấu hình, chưa đếm buổi, chưa duyệt, chưa kiểm tra nộp phụ thu, chưa chuyển lớp và chưa có API học viên đồng ý/từ chối. `new_fee >= current_fee` không chứng minh cấp mới cao hơn; `round` Python và `Math.round` JS còn cần thống nhất quy tắc làm tròn tiền.

**E. Học phí mới nên đi theo đường hóa đơn thực tế của bản đang cài.** `FeeSchedule.create_sales_invoice` tạo Sales Invoice; portal đọc Sales Invoice. Field `fees_doc` của Level Transfer Request lại Link đến `Fees`. Fees vẫn tồn tại nhưng không nên nối nhầm luồng cũ với luồng hóa đơn mới mà chưa thiết kế đối soát. Nên xác định một nguồn khoản phải thu và chứng từ thanh toán rõ ràng.

**F. Test hiện tại chưa là bằng chứng hoàn thành.** `test_level_transfer_request.py` và `test_doct.py` chỉ có lớp test với `pass`. Kiểm tra độc lập trong báo cáo có **12 trường hợp, 11 đúng kỳ vọng và 1 thất bại** (case chồng lấn A); không ghi dữ liệu vào site và không thay thế UAT phân quyền/portal/thanh toán.

### 4.5. Chính xác phần nào dùng lại, phần nào cấu hình, phần nào phải xây

| Loại việc | Thành phần | Kết quả cần có |
|---|---|---|
| Dùng lại | Student, Guardian, Program, Course, Enrollment, Student Group, Room, Instructor | Dữ liệu nền chuẩn hóa; tránh tạo bản sao học viên/lớp/giáo viên/hóa đơn. |
| Dùng lại | Course Schedule/Scheduling Tool, Assessment, Student Attendance, Student Leave Application | Giữ bộ máy lịch/đánh giá/điểm danh, bổ sung quy tắc còn thiếu. |
| Dùng lại | Fee Structure/Schedule, Sales Invoice, Payment Entry, portal Student/Guardian | Thu học phí, giảm giá, chứng từ đã trả/chưa trả, xem kết quả. |
| Cấu hình | 5 Program theo dải band, Course 4 kỹ năng, Academic Term 3 tháng, lịch tuần, bảng giá, Company/Account/Holiday List, vai trò và tài khoản | Dữ liệu cấu hình cho nền tảng chạy theo trung tâm; không hardcode vào controller. |
| Tùy chỉnh | Student/Guardian | Bắt buộc phụ huynh/liên hệ/ngày sinh và định danh duy nhất theo quy định đã chốt. |
| Tùy chỉnh | Room + Course Schedule | Loại phòng cần thiết của buổi, lọc phòng đúng loại còn trống và server kiểm tra lại. |
| Tùy chỉnh | Program Enrollment / Student Group | Cổng đủ học phí; đọc hóa đơn/thu tiền, phân biệt đăng ký chờ với kích hoạt tham gia lớp. |
| Tùy chỉnh | Student Leave Application + Attendance | Deadline, Workflow, đúng giáo viên/buổi/học viên, đơn theo từng buổi và bulk attendance đủ 3 trạng thái. |
| Hoàn thiện mã custom đã có | Level Transfer Request | Xét điều kiện, lấy giá/số buổi, manager approval, student decision, invoice phụ thu, chuyển lớp và lịch sử. |
| Xây mới | IELTS Placement Test + bảng con điểm kỹ năng | Test đầu vào trước xếp lớp, đúng 4 kỹ năng và band, quyết định cấp độ. |
| Xây mới | Instructor Availability + khả năng dạy theo Program/cấp | Giáo viên đăng ký giờ và cấp có thể dạy; dữ liệu cho gợi ý lịch/thay thế. |
| Xây mới | Instructor Leave Request + Workflow | Xin nghỉ dạy, đột xuất, quản lý duyệt/từ chối, lịch sử xử lý. |
| Xây mới | Dịch vụ điều phối lịch và nhật ký buổi gốc/thay/bù/online | Đúng thứ tự ưu tiên, không kéo dài khóa, đếm buổi đã dạy/còn nợ không trùng. Có thể dùng Custom Field/DocType nhật ký thay vì tạo lại Course Schedule. |
| Xây mới | Dịch vụ xét vượt cấp + portal chuyển cấp | Phân tích chuỗi kiểm tra và nhận quyết định học viên, tái sử dụng portal hiện tại. |
| Cấu hình/bổ sung | Notification, báo cáo KPI | Sự kiện đúng người nhận, đo 9 KPI bằng dấu thời gian và kết quả thực tế. |
| Để sau | Zalo | Could have; không coi là khả năng tích hợp đã cài. |

### 4.6. Thứ tự thực hiện và điều kiện nghiệm thu

1. **Chốt nghiệp vụ/dữ liệu nền:** thống nhất band, số buổi khóa, chính sách chưa phản hồi đơn, vai trò quản lý và công thức chuyên cần; sửa các tham chiếu nhầm trong A1. Chốt cấu hình 5 mức phí, kỳ, lớp, giáo viên/phòng và tài khoản.
2. **Khép kín chuỗi tiếp nhận–thu phí–vào lớp:** test đầu vào, hồ sơ phụ huynh, hóa đơn sau giảm, Payment Entry và cổng xếp lớp. Nghiệm thu AC-01/02/10/11; phải thử gọi API khi thiếu tiền.
3. **Lịch/phòng/điểm danh/xin nghỉ:** sửa kiểm tra chồng lấn, thêm khả dụng/loại phòng, quyền đúng giáo viên, hạn 30 phút và mapping trạng thái. Nghiệm thu AC-04/08/09/22–25, cả hai lịch cùng giờ bắt đầu và hai buổi cùng ngày.
4. **Hoàn thiện chuyển cấp:** nguồn giá/số buổi thật, chuỗi điểm, duyệt, portal quyết định và thu phụ thu trước đổi lớp; nghiệm thu AC-12/13 và các nhánh đồng ý/từ chối/không đủ tiền.
5. **Nghỉ dạy và bù:** xây đơn và điều phối bốn phương án, công nợ buổi dạy, thông báo; nghiệm thu AC-18/19/20 và tình huống không được duyệt.
6. **Báo cáo và UAT liên vai trò:** đo K1–K9; kiểm thử bằng quản lý/giáo viên/học viên/phụ huynh, không chỉ Administrator. Điểm phù hợp mã nguồn chỉ là đường cơ sở; cập nhật tỷ lệ theo AC thực sự đạt sau triển khai.

### 4.7. Nội dung A1 cần làm rõ trước khi đóng phạm vi

- **38 BR không đồng nghĩa 38 quy định đã xác nhận.** Các nhãn [CẦN CHỐT] trong A1 vẫn còn hiệu lực.
- **Số buổi:** 3 tháng × 2 buổi/tuần không luôn bằng 24 buổi; 24 hiện là ví dụ và default của controller. Phải chốt số buổi cam kết và ngày kết thúc từng khóa, cách tính buổi bù.
- **Cấp độ:** chốt dải band rời nhau, cách phân vào 7.0–8.0, dưới 3.0 và 8.5/9.0; không tự chọn cách xử lý ngoài bảng giá.
- **Làm tròn:** xác định rõ quy tắc IELTS tại các mốc .25/.75 và quy tắc làm tròn tiền phụ thu; dùng cùng một quy tắc client/server. Chỉ cấu hình Grading Scale không tự làm được việc này.
- **Chưa duyệt đơn nghỉ:** BR-LEAVE-07 chưa chốt; không tự động mặc định chấp thuận/từ chối. A1 cũng cần thống nhất việc tạo Leave ngay khi duyệt với điều kiện học viên thực sự không tham gia.
- **Phân quyền:** quản lý “chỉ xem” đơn nghỉ học là quy tắc ứng dụng; Administrator là tài khoản quản trị đặc quyền, không dùng nó để nghiệm thu vai trò quản lý nghiệp vụ.
- **Chuyên cần:** chốt Leave có tính vào tỷ lệ chuyên cần không và cách xử lý lịch hủy/lùi/chưa diễn ra.
- **Online:** xác định nền tảng/liên kết buổi online và có yêu cầu phòng không; hiện Course Schedule.room bắt buộc nên phải thiết kế cách nới điều kiện khi online.
- **Tham chiếu nhầm:** US-11/AC-11.1 dẫn BR-ENR-01 nhưng nội dung đủ tiền thuộc BR-FEE-03; BR-ENR-01 là hoàn tiền/bảo lưu. US-16 dẫn BR-TR-05 nhưng đề xuất giữa kỳ thuộc BR-TR-01(b).
- **Cổng cơ bản là Must ở phạm vi 2.3**, dù US-15/17 đang ghi Should. Cần thống nhất ưu tiên trước khi làm kế hoạch; báo cáo giữ nhãn nguyên bản của từng US để phép tính kiểm tra lại được.
- **Không tự đưa thêm payroll/online payment/app di động** vào hạng mục cần xây. Hoàn tiền/bảo lưu, nhận giữa khóa, sĩ số tối thiểu/hủy/gộp cần quyết định phạm vi riêng theo BR-ENR.

## Danh mục bằng chứng

''' + evidence_table() + '''

Các nguồn chính thức đối chiếu thêm:

- [Giới thiệu Frappe Education](https://docs.frappe.io/education/introduction).
- [Course Schedule](https://docs.frappe.io/education/course-schedule).
- [Student Leave Application](https://docs.frappe.io/education/student-leave-application).
- [Student Portal](https://docs.frappe.io/education/student-portal).
- [Fees](https://docs.frappe.io/education/fees).
- [DocType Controllers](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers).
- [Hooks và mở rộng lớp từ v16](https://docs.frappe.io/framework/user/en/python-api/hooks#extend-doctype-class).
- [Customizing DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/customize).
- [Database migrations](https://docs.frappe.io/framework/user/en/database-migrations).

Khi tài liệu online và bản đang cài khác nhau, ma trận ưu tiên controller/metadata của các SHA đã kiểm kê. Báo cáo không thay đổi mã nghiệp vụ, cấu hình quyền hoặc dữ liệu vận hành, và chưa commit/push các tệp phân tích lên GitHub.
'''
(out/'BAO_CAO_ANH_XA_LING_IELTS_ERPNEXT.md').write_text(report,encoding='utf-8')

appendix=['# Kiểm kê đầy đủ module và DocType — 08/11/2026',
          '', 'Nguồn: modules.txt và các file định nghĩa DocType của ba app đang cài. Tên giữ nguyên để đối chiếu giao diện/mã nguồn. Số lượng bao gồm bảng con, Single và công cụ; không phải số module nghiệp vụ độc lập.',
          '',module_table(),'', '## Education — toàn bộ 76 DocType', '',
          '| # | DocType | Loại | Nguồn |','|---|---|---|---|']
for i,d in enumerate(inventory['apps']['education']['doctypes'],1):
    kind='Bảng con' if d.get('istable') else 'Single/công cụ cấu hình' if d.get('issingle') else 'Tài liệu thường'
    origin='Dự án' if d['name'] in ('Level Transfer Request','doct') else 'Education gốc'
    appendix.append(f"| {i} | {d['name']} | {kind} | {origin} |")
appendix+=['','## Education — toàn bộ report trong mã nguồn','']
appendix += [f'- `{name}`' for name in inventory['apps']['education']['reports']]
for app in ('frappe','erpnext'):
    info=inventory['apps'][app]
    appendix+=['',f"## {app} — toàn bộ tên DocType theo module",'',f"SHA `{info['sha']}`; {len(info['doctypes'])} định nghĩa."]
    for module in info['modules']:
        group=[d for d in info['doctypes'] if d['module']==module]
        appendix+=['',f'### {module} ({len(group)})','', '; '.join(d['name'] for d in group) or '(Không có định nghĩa DocType trong phạm vi kiểm kê.)']
appendix+=['','## Tùy biến quan sát trên site','',
           '0 Workflow; 0 Client Script; 0 Server Script. Con số này không bao gồm controller Python/JS viết trong app.',
           '', '| DocType | Trường custom | Kiểu | Bắt buộc |','|---|---|---|---|']
for f in inventory['site']['custom_fields']:
    appendix.append(f"| {f['dt']} | {f['fieldname']} | {f['fieldtype']} | {bool(f['reqd'])} |")
(out/'MODULE-INVENTORY.md').write_text('\n'.join(appendix)+'\n',encoding='utf-8')
assert len(mapping)==27 and len({r['id'] for r in mapping})==27
assert len(must)==16
assert Counter(r['current'] for r in mapping)=={.5:17,1:4,0:6}
assert len(set(re.findall(r'^BR-[A-Z]+-\d+$','\n'.join(requirements),flags=re.M)))==38
assert len(re.findall(r'^US-\d+$','\n'.join(requirements),flags=re.M))==27
assert len(inventory['apps']['erpnext']['modules'])==21
assert all((out/path).exists() for _,path,_ in evidence.values())
print(json.dumps(metrics,ensure_ascii=False,indent=2))
print('Report and inventory generated; counts, source links, story IDs and rule count verified.')
