# Nối giờ rảnh giáo viên với Course Schedule

Các tệp này dành cho bản ERPNext/Education đang chạy trong container
`devcontainer-example-frappe-1`, site `school.localhost`.

## 1. Dữ liệu cần chuẩn bị trên web

Trong thanh tìm kiếm ERPNext, tìm đúng tên đối tượng rồi mở danh sách.

1. **Course** và **Program**. Tạo/chọn một môn, ví dụ `IELTS Listening`.
   Tạo/chọn cấp độ `IELTS 5.0–5.5`, thêm môn đó vào bảng **Courses** của Program.
2. **Instructor**. Chọn giáo viên A và đặt Status là **Active**. Ghi lại mã giáo viên
   của hệ thống, ví dụ `EDU-INS-2026-00001`. Các trường Link phải chọn bản ghi thật.
3. **Student Group**. Tạo/chọn lớp. Với lớp mẫu, chọn **Group Based On = Batch**,
   chọn Program ở trên và điền Academic Year/Term phù hợp. Trong bảng **Instructors**, thêm giáo viên A. Muốn gợi ý giáo viên B
   thì cũng phân công B vào bảng này.
4. **Instructor Availability**. Tạo bản ghi cho A, chọn ngày nằm trong kỳ học,
   `from_time = 18:00:00`, `to_time = 20:00:00`, Program giống lớp rồi Save.
5. Có Course và Room để điền các trường bắt buộc khi tạo Course Schedule.

Quy ước của ví dụ này là mỗi bản ghi giờ rảnh thuộc một Program cụ thể.
Program để trống sẽ không khớp. Một khung giờ phải bao trùm trọn buổi học.
Hai khung rảnh liền nhau không được gộp tự động.

Với người dùng ngoài Administrator, cấu hình Role Permission Manager để họ có
quyền đọc Instructor, Student Group, Instructor Availability và quyền tạo/sửa
Course Schedule. Quyền đọc từng Student Group vẫn được kiểm tra. Chỉ cấp các quyền
đó cho vai trò thực sự làm nhiệm vụ xếp lịch.

## 2. Cài phần Python

### Nếu Student Group báo Instructor không tìm thấy giáo viên đã có

Bản Education hiện tại có bộ lọc trong bảng Instructors đưa cả dòng trống và
dòng đang sửa vào danh sách loại trừ. Tệp
`student_group_instructor_filter.client.js` sửa bộ lọc để chỉ loại giáo viên đã
được chọn ở những dòng khác. Bản sửa được lưu thành Client Script riêng trên
Student Group.

Chạy từ thư mục repo để cài bản sửa này:

```powershell
docker cp .\guides\luong_2\student_group_instructor_filter.client.js devcontainer-example-frappe-1:/tmp/student_group_instructor_filter.client.js
docker cp .\guides\luong_2\install_student_group_filter.py devcontainer-example-frappe-1:/tmp/install_student_group_filter.py
docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 /workspace/development/frappe-bench/env/bin/python /tmp/install_student_group_filter.py
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
```

Ghi lại nội dung chưa lưu trước khi tải lại trang bằng Ctrl+Shift+R. Trong bảng
Instructors, chọn giáo viên từ danh sách gợi ý rồi lưu Student Group. Trình cài
sao lưu Client Script cùng tên nếu đã tồn tại trước khi cập nhật.

### Cài kiểm tra giờ rảnh khi xếp lịch

Mở PowerShell ở đúng thư mục repo. Chạy từng lệnh, chờ lệnh trước thành công.

```powershell
cd D:\Projects\educatiionerp\cshttt
docker cp .\guides\luong_2\. devcontainer-example-frappe-1:/tmp/ling-scheduling
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 ./env/bin/python /tmp/ling-scheduling/install.py
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml restart frappe
```

`install.py` kiểm tra fieldname, sao lưu các tệp trước thay đổi rồi chép
`ling_scheduling.py` vào `apps/education/education/ling_scheduling.py`. Script thêm
hook `validate` của Course Schedule vào `education/hooks.py`, giữ các handler đã có.
Chạy lại không nhân đôi hook.

Thông báo cuối bước cài cho biết thư mục bản sao trong
`sites/school.localhost/private/backups/scheduling_code_...`.

Cách đặt module trong Education phù hợp bố trí mã hiện tại của repo. Đây là một
tệp bổ sung của dự án. Khi gửi cho thành viên khác, cần bàn giao cả module, hook
và Client Script. `push.ps1` hiện tại chưa tự thu thập đủ các tệp này.

## 3. Tạo Client Script

### Khôi phục các Client Script đã xuất ngày 15/11/2026

Repo đã có hai DocType trong `custom_doctypes/ielts_placement_test` và
`custom_doctypes/instructor_availability`. Trên máy nhận mã, nạp DocType bằng
`pull.ps1`, cài phần Python theo mục 2, rồi nhập bốn Client Script từ bản xuất:

```powershell
docker cp .\guides\luong_2\client_scripts.json devcontainer-example-frappe-1:/tmp/ling_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost import-doc /tmp/ling_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
```

Lệnh nhập cập nhật các Client Script cùng tên. Bản xuất giữ trạng thái hiện tại:

| Client Script | DocType | Enabled |
|---|---|---|
| Ling IELTS - Student Group Instructor Filter | Student Group | Bật |
| giờ rảnh | Instructor Availability | Bật |
| Lọc giáo viên theo giờ rảnh | Course Schedule | Tắt |
| Tính band | IELTS Placement Test | Bật |

Mỗi Client Script cũng có tệp `.client.js` riêng để đọc và chỉnh sửa:
`student_group_instructor_filter.client.js`, `instructor_availability.client.js`,
`course_schedule.client.js` và `ielts_placement_test.client.js`.

Bật `Lọc giáo viên theo giờ rảnh` khi bắt đầu kiểm thử luồng gợi ý giáo viên.
Các tệp này chứa cấu hình và mã; dữ liệu giáo viên, lớp và giờ rảnh cần được
chuẩn bị theo mục 1. Việc push lên GitHub không triển khai thay đổi lên máy khác.

### Tạo thủ công nếu không nhập bản xuất

1. Mở thanh tìm kiếm, gõ **New Client Script** rồi Enter.
2. Đặt Name là `Ling IELTS - lọc giáo viên theo giờ rảnh` nếu giao diện có ô Name.
3. Chọn **DocType = Course Schedule**. Không chọn Instructor Availability.
4. Chọn **View = Form**, bật **Enabled**.
5. Mở tệp `course_schedule.client.js` cùng thư mục này. Sao chép toàn bộ nội dung
   vào ô **Script**, bấm Save.
6. Mở lại Course Schedule và nhấn **Ctrl+Shift+R** để tải lại mã trên trình duyệt.

`frm.set_query` khai báo hàm tìm kiếm Python của trường Instructor. Khi mở hoặc
gõ trong ô Instructor, Frappe tự gửi lớp, ngày, giờ lên server và lấy kết quả.
Client Script cài bộ lọc sau bước onload của script chuẩn. Phần Python tiếp tục
giới hạn theo bảng Instructors của lớp.

## 4. Thử tạo lịch

1. Tìm **Course Schedule**, mở danh sách và bấm Add Course Schedule/New.
2. Chọn **Student Group** đã chuẩn bị.
3. Chọn Course và Room.
4. Chọn **Schedule Date** đúng ngày trong Instructor Availability.
5. Nhập **From Time = 18:30:00**, **To Time = 19:30:00**.
6. Sau khi điền bốn dữ liệu lớp/ngày/từ giờ/đến giờ, bấm ô **Instructor**. Có thể
   gõ tên A để tìm. A xuất hiện khi còn Active, đúng phân công, đúng Program,
   đủ giờ rảnh và chưa có lịch khác giao nhau.
7. Chọn A và bấm Save. Server kiểm tra lại trước khi lưu.

Khi sửa một lịch đã lưu, tìm kiếm loại trừ chính lịch đó khỏi kiểm tra bận.
Các lịch cũ chỉ thay đổi trường ngoài lớp/ngày/giờ/giáo viên tiếp tục dùng hành vi
cũ. Quy tắc mới áp dụng khi tạo lịch hoặc sửa một trong các trường xếp lịch.

## 5. Kết quả mong đợi

| Tình huống | Kết quả |
|---|---|
| A rảnh 18–20h, chọn buổi 18:30–19:30, cùng ngày/Program | Có A trong danh sách |
| Chọn buổi 19–21h | A bị loại vì giờ rảnh không bao trùm |
| Chọn ngày khác hoặc Program khác | A bị loại |
| A chưa được phân công trong Student Group | A bị loại |
| A đã có buổi khác 18–20h, đang tạo thêm buổi 18–19h | A bị loại dù cùng giờ bắt đầu |
| Buổi cũ kết thúc đúng lúc buổi mới bắt đầu | Không coi là trùng |
| Sửa giờ của chính bản ghi hiện tại, vẫn trong giờ rảnh | Không tự coi lịch đó là lịch bận khác |
| Chọn A trước, sau đó sửa giờ ra ngoài giờ rảnh rồi Save | Server chặn lưu |

## 6. Nếu danh sách giáo viên trống

Kiểm tra lần lượt bốn ô lớp/ngày/từ giờ/đến giờ, Program của lớp, bảng Instructors
của lớp, trạng thái Active của giáo viên, ngày và Program của giờ rảnh, rồi lịch
đã xếp. Với tài khoản khác Administrator, kiểm tra quyền đọc các DocType liên quan.

Các lỗi thường gặp:

| Lỗi | Cách xử lý |
|---|---|
| No module named education.ling_scheduling | Chạy lại bước chép tệp và install.py, rồi restart frappe |
| Bạn cần quyền đọc Instructor Availability | Cấp quyền đọc cho đúng vai trò xếp lịch |
| Hãy phân công giáo viên... | Thêm giáo viên vào bảng Instructors trong Student Group |
| Hãy chọn Program cho lớp... | Điền Program trên Student Group |
| Hãy chọn ngày học... | Điền đủ ngày và hai mốc giờ |

Hook giữ kiểm tra chuẩn của Course Schedule. Ví dụ bổ sung kiểm tra bận của giáo
viên trên Course Schedule và Assessment Plan, kể cả vai trò giám sát/chấm thi.
Các lần lưu Course Schedule qua hook dùng khóa hàng Instructor và đọc lại lịch
để hai thao tác xếp cùng giáo viên không cùng vượt qua kiểm tra. Các quy trình
ghi lịch bên ngoài hook hoặc tạo Assessment Plan có thể cần phối hợp khóa nếu
hệ thống được mở rộng để xử lý đặt lịch đồng thời qua nhiều nguồn.

## 7. Luồng gọi hàm

```text
Điền lớp + ngày + giờ
       |
Mở ô Instructor trên Course Schedule
       |
Client Script gọi query education.ling_scheduling.instructor_query
       |
Lấy giáo viên đã phân công cho lớp
       |
Giữ các giáo viên có giờ rảnh đúng Program và bao trùm buổi học
       |
Loại giáo viên đã có lịch học/kiểm tra giao nhau
       |
Trả mã và tên giáo viên để người dùng chọn
       |
Save gọi validate_course_schedule để kiểm tra lại
```

Nguồn API chính thức:

- https://docs.frappe.io/framework/user/en/api/form
- https://docs.frappe.io/framework/user/en/python-api/hooks
- https://docs.frappe.io/framework/user/en/guides/app-development/overriding-link-query-by-custom-script
