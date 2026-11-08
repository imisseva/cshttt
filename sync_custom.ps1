# Script đồng bộ các Custom DocType vào hệ thống Frappe Docker
Write-Host "Dang dong bo Custom DocTypes vao he thong..." -ForegroundColor Cyan

docker exec -w /workspace devcontainer-example-frappe-1 bash -c "mkdir -p /workspace/development/frappe-bench/apps/education/education/education/doctype/ && cp -r /workspace/custom_doctypes/* /workspace/development/frappe-bench/apps/education/education/education/doctype/ && cd /workspace/development/frappe-bench && bench --site school.localhost migrate"

Write-Host "Da dong bo thanh cong! Ban hay vao trinh duyet kiem tra." -ForegroundColor Green
