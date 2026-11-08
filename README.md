# Dự án ERPNext - Module Education (Version 16)

Hệ thống quản lý giáo dục & trường học chạy trên nền tảng **ERPNext v16** và **Frappe Framework v16** thông qua Docker.

## 📦 Thành phần hệ thống

- **Frappe Framework:** `version-16` (Python 3.14)
- **ERPNext:** `version-16`
- **Frappe Education:** `version-16`
- **Database:** MariaDB 11.8
- **Cache/Queue:** Redis

---

## 🚀 Hướng dẫn cài đặt & chạy trên máy mới

### 1. Yêu cầu trước khi cài
- Đã cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/) trên máy tính và đang bật.
- Đã cài [Git](https://git-scm.com/).

### 2. Khởi động môi trường Docker
Mở PowerShell / Terminal tại thư mục gốc của dự án và chạy:

```powershell
docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml up -d
```

### 3. Khởi tạo Site và cài đặt ứng dụng (Chỉ chạy lần đầu tiên)
Chạy lệnh tự động cài đặt Frappe, ERPNext và Education v16 vào site:

```powershell
docker exec devcontainer-example-frappe-1 python3 installer.py -j apps.json -t version-16 -p 3.14.8 -s school.localhost -a admin
```

### 4. Khởi động dịch vụ Web
```powershell
docker exec -d -w /workspace/development/frappe-bench devcontainer-example-frappe-1 /home/frappe/.local/bin/bench start
```

---

## 🌐 Truy cập hệ thống

- **Đường dẫn (URL):** [http://localhost:8000/app](http://localhost:8000/app)
- **Tài khoản (Username):** `Administrator`
- **Mật khẩu (Password):** `admin`

---

## 🛠️ Quản lý hệ thống

* **Dừng hệ thống:**
  ```powershell
  docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml stop
  ```

* **Bật lại hệ thống:**
  ```powershell
  docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml start
  docker exec -d -w /workspace/development/frappe-bench devcontainer-example-frappe-1 /home/frappe/.local/bin/bench start
  ```

* **Sao lưu dữ liệu (Backup):**
  ```powershell
  docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost backup --with-files
  ```
