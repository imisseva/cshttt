# Luồng 4 — Theo dõi thu học phí & chặn ghi danh khi chưa đóng đủ

Các tệp này dành cho bản ERPNext/Education đang chạy trong container
`devcontainer-example-frappe-1`, site `school.localhost`.

Quy tắc **BR-FEE-03** của Ling IELTS yêu cầu **bắt buộc đóng đủ 100% học phí mới
được xếp vào lớp**. Phần tùy biến ở đây thêm validation trên **Student Group**:
khi lưu, hệ thống kiểm tra từng học viên đã có chứng từ `Fees` đã Submit với
`outstanding_amount == 0` chưa; nếu chưa thì chặn lưu.

## 1. Dữ liệu cần chuẩn bị trên web

1. **Fee Category / Fee Structure / Fees**. Tạo chứng từ `Fees` cho học viên theo
   cấp độ đăng ký, rồi thu tiền qua **Payment Entry** sao cho `outstanding_amount`
   về 0.
2. **Student Group**. Tạo/chọn lớp, đặt **Program** (nếu có) và thêm học viên vào
   bảng **Students**.

Quy ước của phần kiểm tra:

- Lớp có **Program**: học viên phải có chứng từ `Fees` (đã Submit, hết nợ) thuộc
  đúng Program của lớp.
- Lớp chưa có **Program**: chỉ cần một chứng từ `Fees` đã Submit và hết nợ.

## 2. Cài phần Python

Mở PowerShell ở đúng thư mục repo. Chạy từng lệnh, chờ lệnh trước thành công.

```powershell
cd D:\fourth1st\HTTT DN\proj\proj\cshttt
docker cp .\guides\luong_4\. devcontainer-example-frappe-1:/tmp/ling-fees
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 ./env/bin/python /tmp/ling-fees/install.py
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml restart frappe
```

`install.py` chép `ling_fees.py` vào `apps/education/education/ling_fees.py` và đăng
ký hook `validate` cho Student Group. Chạy lại không nhân đôi hook. Bản sao mã trước
thay đổi được lưu trong `sites/school.localhost/private/code_backups/fees_code_...`.

## 3. Tạo Client Script

Nhập bản xuất Client Script nút kiểm tra học phí:

```powershell
docker cp .\guides\luong_4\client_scripts.json devcontainer-example-frappe-1:/tmp/ling_fees_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost import-doc /tmp/ling_fees_client_scripts.json
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost clear-cache
```

| Client Script | DocType | Enabled |
|---|---|---|
| Kiểm tra học phí Student Group | Student Group | Bật |

Client Script thêm nút **Kiểm tra học phí** để xem nhanh còn nợ của từng học viên
mà không cần chờ lưu. Nếu nhập tay, dán toàn bộ `student_group_fee.client.js`.

## 4. Thử kiểm thử

1. Tạo một `Fees` cho học viên A nhưng chưa thu (outstanding > 0).
2. Tạo `Fees` cho học viên B và thu đủ (outstanding = 0).
3. Tạo **Student Group**, thêm cả A và B vào bảng **Students**, bấm Save.

## 5. Kết quả mong đợi

| Tình huống | Kết quả |
|---|---|
| Lớp gồm A (còn nợ) và B (đã đóng đủ) | Server chặn lưu, liệt kê A chưa đóng đủ (BR-FEE-03) |
| Lớp chỉ gồm B | Lưu thành công |
| Bấm nút **Kiểm tra học phí** | Hiện còn nợ và trạng thái từng học viên |
| Học viên có Fees khác Program (lớp đã đặt Program) | Bị xem là chưa đóng đủ |

## 6. Lưu ý

- Hook chỉ chạy trên Student Group. Nếu quy trình ghi danh của bạn dùng
  `Program Enrollment` trực tiếp, cần thêm hook tương tự cho DocType đó.
- Muốn tạm tắt để nhập dữ liệu hàng loạt, chỉnh `enabled` của Client Script hoặc
  tạm bỏ hook trong `education/hooks.py`, rồi bật lại trước khi vận hành thật.

## 7. Kiểm thử tự động

Chạy script `test_ling_fees.py` (tự tạo học viên + chứng từ Fees rồi dọn dẹp):

```powershell
docker cp .\guides\luong_4\test_ling_fees.py devcontainer-example-frappe-1:/tmp/ling-fees/test_ling_fees.py
docker exec -w /workspace/development/frappe-bench/sites devcontainer-example-frappe-1 /workspace/development/frappe-bench/env/bin/python /tmp/ling-fees/test_ling_fees.py
```

Kết quả mong đợi cuối script: `10 PASS, 0 FAIL`. Hướng dẫn test tay chi tiết qua
frontend xem tại [docs/huong_dan_test_thu_cong_luong_3_4.md](../../docs/huong_dan_test_thu_cong_luong_3_4.md).
