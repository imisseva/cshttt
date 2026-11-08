# Script đồng bộ các Custom DocType và Tùy biến vào hệ thống Frappe Docker
Write-Host "Dang dong bo Custom DocTypes va Customizations vao he thong..." -ForegroundColor Cyan

docker exec -w /workspace devcontainer-example-frappe-1 bash -c "mkdir -p /workspace/development/frappe-bench/apps/education/education/education/doctype/ && cp -r /workspace/custom_doctypes/level_transfer_request /workspace/development/frappe-bench/apps/education/education/education/doctype/ 2>/dev/null || true; mkdir -p /workspace/development/frappe-bench/apps/education/education/education/custom/ && cp -r /workspace/custom_doctypes/custom/* /workspace/development/frappe-bench/apps/education/education/education/custom/ 2>/dev/null || true; cd /workspace/development/frappe-bench && bench --site school.localhost migrate"

Write-Host "Da dong bo thanh cong! Ban hay vao trinh duyet kiem tra." -ForegroundColor Green
