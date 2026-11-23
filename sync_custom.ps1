$ErrorActionPreference = "Stop"

Write-Host "Dang dong bo app ling_ielts vao he thong Frappe Docker..." -ForegroundColor Cyan

$syncCmd = @'
set -e
cd /workspace/development/frappe-bench
if ! ./env/bin/python -c "import ling_ielts" >/dev/null 2>&1; then
    ./env/bin/pip install --no-deps -e apps/ling_ielts
fi
if ! grep -qx "ling_ielts" sites/apps.txt; then
    echo "ling_ielts" >> sites/apps.txt
fi
if ! bench --site school.localhost list-apps | grep -Eq "(^|[[:space:]])ling_ielts([[:space:]]|$)"; then
    bench --site school.localhost install-app ling_ielts
fi
bench --site school.localhost migrate
bench build --app ling_ielts
bench --site school.localhost clear-cache
'@

$syncCmdUnix = $syncCmd -replace "`r`n", "`n"
docker exec -i devcontainer-example-frappe-1 bash -lc $syncCmdUnix
if ($LASTEXITCODE -ne 0) { throw "Dong bo app ling_ielts trong Docker that bai." }

Write-Host "Da dong bo app ling_ielts thanh cong! Ban hay vao trinh duyet kiem tra (Ctrl+Shift+R)." -ForegroundColor Green
