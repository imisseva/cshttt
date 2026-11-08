# Dự án ERPNext - Module Education (Version 16)

Hệ thống quản lý giáo dục & trường học chạy trên nền tảng **ERPNext v16** và **Frappe Framework v16** thông qua Docker cho case study **Ling IELTS**.

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

### 5. Nạp các Custom DocType & Tùy biến
```powershell
.\pull.ps1
```

* Truy cập web tại: **[http://localhost:8000/app](http://localhost:8000/app)** (Tài khoản: `Administrator` / `admin`).

---

## 🔄 QUY TRÌNH LÀM VIỆC NHÓM (HÀNG NGÀY)

Quy trình cực kỳ đơn giản với 2 lệnh tự động:

### 📤 1. Khi bạn làm xong và muốn gửi lên cho bạn bè:
Sau khi bạn thêm DocType, cấu hình trường, bấm Save / Export Customizations xong trên web, mở PowerShell gõ:
```powershell
.\push.ps1 "Mô tả những gì bạn vừa làm"
```
*(Script sẽ tự động gom toàn bộ cấu hình mới và đẩy thẳng lên GitHub).*

### 📥 2. Khi bạn của bạn muốn nhận cập nhật mới về máy:
Bạn của bạn mở PowerShell tại thư mục dự án và chỉ cần gõ đúng 1 lệnh:
```powershell
.\pull.ps1
```
*(Script sẽ tự động kéo code từ GitHub về, nạp vào Docker và cập nhật Database trong vài giây).*

---

## 🛠️ Quản lý hệ thống cơ bản

* **Dừng Docker khi nghỉ làm:**
  ```powershell
  docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml stop
  ```

* **Bật lại Docker khi tiếp tục làm:**
  ```powershell
  docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml start
  docker exec -d -w /workspace/development/frappe-bench devcontainer-example-frappe-1 /home/frappe/.local/bin/bench start
  ```
