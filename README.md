# Dự án ERPNext - Module Education (Version 16)

Hệ thống quản lý giáo dục & trường học chạy trên nền tảng **ERPNext v16** và **Frappe Framework v16** thông qua Docker cho case study **Ling IELTS**.

## Bổ sung ngày 15/11/2026

- Hai DocType: **IELTS Placement Test** và **Instructor Availability**.
- Mã Python kiểm tra giờ rảnh, phân công và trùng lịch khi lưu Course Schedule.
- Client Script tính band IELTS, kiểm tra giờ rảnh, sửa bộ lọc Instructor và bản xuất bốn Client Script.
- [Hướng dẫn cài đặt và kiểm thử luồng xếp lịch](guides/luong_2/README.md).
- [Luồng 3 — Phân bổ phòng học theo loại phòng](guides/luong_3/README.md).
- [Luồng 4 — Chặn ghi danh khi chưa đóng đủ học phí](guides/luong_4/README.md).
- [Hướng dẫn test tay Luồng 3 & 4 qua frontend](docs/huong_dan_test_thu_cong_luong_3_4.md).

Client Script lọc giáo viên theo giờ rảnh trên Course Schedule đang tắt trong
bản xuất; bật lại khi kiểm thử theo hướng dẫn. Chạy `pull.ps1` để nạp DocType,
sau đó làm các bước cài Python và nhập Client Script trong tài liệu luồng xếp lịch.

## 📦 Thành phần hệ thống

- **Frappe Framework:** `version-16` (Python 3.14)
- **ERPNext:** `version-16`
- **Frappe Education:** `version-16`
- **Database:** MariaDB 11.8
- **Cache/Queue:** Redis

---

## 🚀 Hướng dẫn cho thành viên mới (Cài đặt lần đầu)

### 1. Chuẩn bị
- Đã cài và bật [Docker Desktop](https://www.docker.com/products/docker-desktop/) trên máy tính.
- Clone repository về máy:
  ```bash
  git clone https://github.com/imisseva/cshttt.git
  cd cshttt
  ```

### 2. Khởi động môi trường Docker
```powershell
docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml up -d
```

### 3. Khởi tạo Site ban đầu
```powershell
docker exec devcontainer-example-frappe-1 python3 installer.py -j apps.json -t version-16 -p 3.14.8 -s school.localhost -a admin
```

### 4. Khởi động dịch vụ Web
```powershell
docker exec -d -w /workspace/development/frappe-bench devcontainer-example-frappe-1 /home/frappe/.local/bin/bench start
```

### 5. Nạp toàn bộ dữ liệu & DocType mới nhất
```powershell
.\import_data.ps1
```

* Truy cập web tại: **[http://localhost:8000/app](http://localhost:8000/app)** (Tài khoản: `Administrator` / `admin`).

---

## 🔄 BỘ LỆNH ĐỒNG BỘ LÀM VIỆC NHÓM HÀNG NGÀY

### 1. Đồng bộ Cấu trúc (DocType mới, Sửa Form, Custom Fields)
* **Người gửi:**
  ```powershell
  .\push.ps1 "Mô tả việc bạn vừa làm"
  ```
* **Người nhận:**
  ```powershell
  .\pull.ps1
  ```

### 2. Đồng bộ DỮ LIỆU (Học sinh, Điểm thi, Lịch học, Học phí)
* **Người vừa nhập xong dữ liệu:**
  ```powershell
  .\export_data.ps1 "Mo ta du lieu vua nhap"
  ```
  *(Tự động sao lưu database ~1MB và đẩy lên GitHub).*
* **Người nhận muốn nạp toàn bộ dữ liệu về máy mình:**
  ```powershell
  .\import_data.ps1
  ```
  *(Tự động kéo về và phục hồi 100% dữ liệu vào MariaDB).*

---

## 🛠️ Quản lý hệ thống cơ bản

* **Khi muốn nghỉ:**
  ```powershell
  .\stop.ps1
  ```

* **Khi muốn làm tiếp:**
  ```powershell
  .\start.ps1
  ```
