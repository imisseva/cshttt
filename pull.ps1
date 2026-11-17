Write-Host "[1/2] Dang keo cap nhat moi nhat tu GitHub..." -ForegroundColor Cyan
git pull origin main

Write-Host "[2/2] Dang dong bo cac DocType vao Docker va cap nhat Database..." -ForegroundColor Cyan

$destDocTypes = "frappe_docker\development\frappe-bench\apps\education\education\education\doctype"
$destCustom = "frappe_docker\development\frappe-bench\apps\education\education\education\custom"

if (Test-Path "custom_doctypes") {
    Get-ChildItem -Directory -Path "custom_doctypes" | Where-Object { $_.Name -ne "custom" } | ForEach-Object {
        $targetDir = Join-Path $destDocTypes $_.Name
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        Copy-Item -Recurse -Force "$($_.FullName)\*" "$targetDir\"
    }
    if (Test-Path "custom_doctypes\custom") {
        New-Item -ItemType Directory -Force -Path $destCustom | Out-Null
        Copy-Item -Recurse -Force "custom_doctypes\custom\*" "$destCustom\"
    }
}

docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost migrate

Write-Host "HOAN TAT! Toan bo DocType va cau hinh moi da duoc cap nhat vao may cua ban." -ForegroundColor Green
Write-Host "Hay mo trinh duyet (http://localhost:8000/app) de tiep tuc lam viec nhe!" -ForegroundColor Yellow
