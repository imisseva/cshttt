param(
    [string]$message = "backup and export database"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/2] Dang sao luu toan bo Co so du lieu (MariaDB)..." -ForegroundColor Cyan

# 1. Chay lenh bench backup tren Docker
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost backup
if ($LASTEXITCODE -ne 0) { throw "Khong tao duoc backup; da dung export." }

# 2. Copy file backup moi nhat ra data_backup/database.sql.gz
New-Item -ItemType Directory -Force -Path data_backup | Out-Null
$backupDir = "/workspace/development/frappe-bench/sites/school.localhost/private/backups"
$latestBackup = docker exec devcontainer-example-frappe-1 bash -lc "ls -1t $backupDir/*database.sql.gz | head -n 1"
if ($LASTEXITCODE -ne 0 -or -not $latestBackup) { throw "Khong tim thay backup trong container." }
$latestBackup = ([string]$latestBackup).Trim()
if (-not $latestBackup.StartsWith("$backupDir/") -or -not $latestBackup.EndsWith("database.sql.gz")) {
    throw "Duong dan backup khong hop le."
}
docker cp "devcontainer-example-frappe-1:$latestBackup" "data_backup\database.sql.gz"
if ($LASTEXITCODE -ne 0) { throw "Khong chep duoc backup tu container." }
if ((Get-Item "data_backup\database.sql.gz").Length -eq 0) { throw "Backup rong; da dung export." }
$fileSize = [math]::Round((Get-Item "data_backup\database.sql.gz").Length / 1MB, 2)
Write-Host "  -> Da sao luu thanh cong: data_backup\database.sql.gz ($fileSize MB)" -ForegroundColor Green

# 3. Gom ca DocType/Customizations va day toan bo len GitHub
Write-Host "[2/2] Dang dong bo ca DocType va Co so du lieu len GitHub..." -ForegroundColor Cyan
git add data_backup\database.sql.gz export_data.ps1
if ($LASTEXITCODE -ne 0) { throw "Khong stage duoc backup." }
& (Join-Path $PSScriptRoot "push.ps1") -message $message
if ($LASTEXITCODE -ne 0) { throw "Khong day duoc backup len GitHub." }

Write-Host "HOAN TAT! Toan bo du lieu va code da duoc day len GitHub thanh cong." -ForegroundColor Green
