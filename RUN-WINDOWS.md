# Chạy trên Windows

Repo: `D:\Projects\educatiionerp\cshttt`

Môi trường này dùng `compose.windows.yaml` để lưu bench và thư viện trong Docker
volume `devcontainer-example_bench-data`, tránh tốc độ chậm của bind mount Windows.
Dữ liệu MariaDB nằm trong volume `devcontainer-example_mariadb-data`.

## Bật lại sau khi đã cài đặt

Mở Docker Desktop, sau đó chạy PowerShell tại thư mục repo:

```powershell
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml up -d
```

Web: <http://localhost:8000/app>

- Tài khoản: `Administrator`
- Mật khẩu: `admin`
- Site: `school.localhost`

## Xem log

```powershell
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml logs --tail 100 frappe
```

## Dừng

```powershell
docker compose -f frappe_docker/devcontainer-example/docker-compose.yml -f compose.windows.yaml stop
```

Giữ Docker volumes để bảo toàn dữ liệu và thư viện đã cài. Không dùng `down -v`
nếu muốn giữ môi trường này.

## Sao lưu

```powershell
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost backup --with-files
```
