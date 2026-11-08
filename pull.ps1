Write-Host "📥 1. Dang keo cap nhat moi nhat tu GitHub..." -ForegroundColor Cyan
git pull origin main

Write-Host "🔄 2. Dang dong bo vao he thong va cap nhat Database..." -ForegroundColor Cyan
docker exec -w /workspace devcontainer-example-frappe-1 bash -c "mkdir -p /workspace/development/frappe-bench/apps/education/education/education/doctype/ && cp -r /workspace/custom_doctypes/level_transfer_request /workspace/development/frappe-bench/apps/education/education/education/doctype/ 2>/dev/null || true; mkdir -p /workspace/development/frappe-bench/apps/education/education/education/custom/ && cp -r /workspace/custom_doctypes/custom/* /workspace/development/frappe-bench/apps/education/education/education/custom/ 2>/dev/null || true; cd /workspace/development/frappe-bench && bench --site school.localhost migrate"

Write-Host "🎉 HOAN TAT! Toan bo DocType va cau hinh moi da duoc cap nhat vao may cua ban." -ForegroundColor Green
Write-Host "👉 Ban hay mo trinh duyet (http://localhost:8000/app) de tiep tuc lam viec nhe!" -ForegroundColor Yellow
