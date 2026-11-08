param(
    [string]$message = "backup and export database"
)

Write-Host "📦 1. Dang sao luu toan bo Co so du lieu (MariaDB)..." -ForegroundColor Cyan

# 1. Chay lenh bench backup tren Docker
docker exec -w /workspace/development/frappe-bench devcontainer-example-frappe-1 bench --site school.localhost backup

# 2. Copy file backup moi nhat ra data_backup/database.sql.gz
New-Item -ItemType Directory -Force -Path data_backup | Out-Null
$backupDir = "frappe_docker\development\frappe-bench\sites\school.localhost\private\backups"
if (Test-Path $backupDir) {
    $latestBackup = Get-ChildItem -Path $backupDir -Filter "*database.sql.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestBackup) {
        Copy-Item -Force $latestBackup.FullName "data_backup\database.sql.gz"
        $fileSize = [math]::Round((Get-Item "data_backup\database.sql.gz").Length / 1MB, 2)
        Write-Host "  -> Da sao luu thanh cong: data_backup\database.sql.gz ($fileSize MB)" -ForegroundColor Green
    }
}

# 3. Gom ca DocType/Customizations va day toan bo len GitHub
Write-Host "🚀 2. Dang dong bo ca DocType va Co so du lieu len GitHub..." -ForegroundColor Cyan
git add data_backup\database.sql.gz
.\push.ps1 $message

Write-Host "🎉 HOAN TAT! Toan bo du lieu va code da duoc day len GitHub thanh cong." -ForegroundColor Green
