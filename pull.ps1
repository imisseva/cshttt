$ErrorActionPreference = "Stop"

Write-Host "[1/2] Dang keo cap nhat moi nhat tu GitHub..." -ForegroundColor Cyan
git pull origin main
if ($LASTEXITCODE -ne 0) { throw "Git pull that bai." }

Write-Host "[2/2] Dang dong bo app ling_ielts vao Docker va cap nhat Database..." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "sync_custom.ps1")

Write-Host "HOAN TAT! Toan bo app ling_ielts va cau hinh moi da duoc cap nhat vao may cua ban." -ForegroundColor Green
Write-Host "Hay mo trinh duyet (http://localhost:8000/app) de tiep tuc lam viec nhe!" -ForegroundColor Yellow
