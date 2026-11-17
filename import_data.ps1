Write-Host "[1/2] Dang keo du lieu moi nhat tu GitHub ve may..." -ForegroundColor Cyan
git pull origin main

if (-not (Test-Path "data_backup\database.sql.gz")) {
    Write-Host "Khong tim thay file data_backup\database.sql.gz de phuc hoi!" -ForegroundColor Red
    exit 1
}

Write-Host "[2/2] Dang phuc hoi toan bo Co so du lieu vao he thong Docker..." -ForegroundColor Cyan

# 1. Copy file backup vao container va chay restore database
docker cp data_backup\database.sql.gz devcontainer-example-frappe-1:/tmp/database.sql.gz
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bash -c "bench --site school.localhost restore /tmp/database.sql.gz --mariadb-root-password 123 --admin-password admin --force && rm -f /tmp/database.sql.gz"

# 2. Dong bo lai cac custom doctypes neu co
powershell -ExecutionPolicy Bypass -File .\pull.ps1

Write-Host "HOAN TAT! Toan bo du lieu hoc sinh, lop hoc, diem so da duoc phuc hoi 100% vao may cua ban." -ForegroundColor Green
Write-Host "Hay mo trinh duyet (http://localhost:8000/app) de kiem tra nhe!" -ForegroundColor Yellow
