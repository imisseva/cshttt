Write-Host "📥 1. Dang keo cap nhat moi nhat tu GitHub..." -ForegroundColor Cyan
git pull origin main

Write-Host "🔄 2. Dang dong bo cac DocType vao Docker va cap nhat Database..." -ForegroundColor Cyan

docker exec -w /workspace devcontainer-example-frappe-1 bash -c "
for d in /workspace/custom_doctypes/*/; do
    name=\$(basename \"\$d\")
    if [ \"\$name\" != \"custom\" ]; then
        mkdir -p \"/workspace/development/frappe-bench/apps/education/education/education/doctype/\$name\"
        cp -r \"\$d\"* \"/workspace/development/frappe-bench/apps/education/education/education/doctype/\$name/\" 2>/dev/null || true
    fi
done
mkdir -p /workspace/development/frappe-bench/apps/education/education/education/custom/
cp -r /workspace/custom_doctypes/custom/* /workspace/development/frappe-bench/apps/education/education/education/custom/ 2>/dev/null || true
cd /workspace/development/frappe-bench && bench --site school.localhost migrate
"

Write-Host "🎉 HOAN TAT! Toan bo DocType va cau hinh moi da duoc cap nhat vao may cua ban." -ForegroundColor Green
Write-Host "👉 Hay mo trinh duyet (http://localhost:8000/app) de tiep tuc lam viec nhe!" -ForegroundColor Yellow
