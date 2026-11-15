# Luồng 3 — Phân bổ phòng học theo loại phòng

Các tệp này dành cho bản ERPNext/Education đang chạy trong container
`devcontainer-example-frappe-1`, site `school.localhost`.

Luồng này dựa trên hai Custom Field đã có trong repo:

- `Room.custom_room_type` (Select: `Phòng giảng dạy` / `Phòng Speaking` / `Phòng Listening`).
- `Course.custom_required_room_type` (Select cùng bộ giá trị).

Quy tắc **BR-ROOM-01** (không xếp trùng phòng cùng khung giờ) đã có sẵn trong
`CourseSchedule.validate_overlap()`. Phần tùy biến ở đây chỉ bổ sung **BR-ROOM-02**:
buổi học phải dùng đúng loại phòng mà môn học yêu cầu.

## 1. Dữ liệu cần chuẩn bị trên web

1. **Room**. Với từng phòng, đặt trường **Room Type**:
   - Phòng thường → `Phòng giảng dạy`.
   - Phòng có tai nghe → `Phòng Listening`.
   - Phòng phỏng vấn nói → `Phòng Speaking`.
2. **Course**. Với từng môn, đặt trường **Required Room Type**:
   - `IELTS Listening` → `Phòng Listening`.
   - `IELTS Speaking` → `Phòng Speaking`.
   - `IELTS Reading` / `IELTS Writing` → `Phòng giảng dạy`.
3. **Course Schedule**. Chọn **Course** rồi mở ô **Room** để xem danh sách được lọc.

## 2. Cài phần Python

Mở PowerShell ở đúng thư mục repo. Chạy từng lệnh, chờ lệnh trước thành công.

```powershell
cd D:\fourth1st\HTTT DN\proj\proj\cshttt
docker cp .\guides\luong_3\. devcontainer-example-frappe-1:/tmp/ling-room
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 ./env/bin/python /tmp/ling-room/install.py
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml restart frappe
```

`install.py` chép `ling_room.py` vào `apps/education/education/ling_room.py` và đăng
ký thêm hook `validate` của Course Schedule, **giữ nguyên** các handler đã có (kể cả
handler giờ rảnh giáo viên của Luồng 2). Chạy lại không nhân đôi hook. Bản sao mã
trước thay đổi được lưu trong `sites/school.localhost/private/code_backups/room_code_...`.

## 3. Tạo Client Script

Nhập bản xuất Client Script lọc phòng:

```powershell
docker cp .\guides\luong_3\client_scripts.json devcontainer-example-frappe-1:/tmp/ling_room_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost import-doc /tmp/ling_room_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
```

| Client Script | DocType | Enabled |
|---|---|---|
| Lọc phòng theo loại phòng | Course Schedule | Bật |

Nếu nhập tay, tạo **New Client Script** với `dt = Course Schedule`, `view = Form`,
`enabled = 1`, rồi dán toàn bộ nội dung `course_schedule_room.client.js`.

## 4. Thử tạo lịch

1. Tìm **Course Schedule**, mở danh sách và bấm Add Course Schedule/New.
2. Chọn **Student Group**, **Course** (ví dụ `IELTS Listening`).
3. Bấm ô **Room**. Danh sách chỉ còn các phòng loại `Phòng Listening`.
4. Chọn một phòng đúng loại rồi Save.

## 5. Kết quả mong đợi

| Tình huống | Kết quả |
|---|---|
| Course yêu cầu `Phòng Listening`, mở ô Room | Chỉ thấy phòng loại Listening |
| Course chưa đặt Required Room Type | Thấy toàn bộ phòng |
| Chọn phòng sai loại rồi Save | Server chặn lưu, báo BR-ROOM-02 |
| Hai buổi trùng phòng cùng khung giờ | ERPNext chặn sẵn (BR-ROOM-01) |

## 6. Nếu danh sách phòng trống

Kiểm tra lần lượt: đã chọn Course, Course có đặt **Required Room Type**, đã có phòng
nào được đặt đúng **Room Type** chưa, rồi quyền đọc Room của tài khoản.

| Lỗi | Cách xử lý |
|---|---|
| No module named education.ling_room | Chạy lại bước chép tệp và install.py, rồi restart frappe |
| Ô Room hiện toàn bộ phòng | Client Script chưa bật hoặc chưa tải lại trang (Ctrl+Shift+R) |

## 7. Kiểm thử tự động

Chạy script `test_ling_room.py` (tự tạo dữ liệu test rồi dọn dẹp):

```powershell
docker cp .\guides\luong_3\test_ling_room.py devcontainer-example-frappe-1:/tmp/ling-room/test_ling_room.py
docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 /workspace/development/frappe-bench/env/bin/python /tmp/ling-room/test_ling_room.py
```

Kết quả mong đợi cuối script: `9 PASS, 0 FAIL`. Hướng dẫn test tay chi tiết qua
frontend xem tại [docs/huong_dan_test_thu_cong_luong_3_4.md](../../docs/huong_dan_test_thu_cong_luong_3_4.md).
