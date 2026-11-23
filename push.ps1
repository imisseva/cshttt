param(
    [string]$message = "update ling_ielts app"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/2] Dang gom ma nguon app ling_ielts va cac script dong bo..." -ForegroundColor Cyan

$appPath = "frappe_docker/development/frappe-bench/apps/ling_ielts"
if (-not (Test-Path $appPath)) {
    throw "Khong tim thay thu muc app: $appPath"
}

git add -- $appPath README.md push.ps1 pull.ps1 sync_custom.ps1
if ($LASTEXITCODE -ne 0) { throw "Khong stage duoc thay doi." }

Write-Host "[2/2] Dang day len GitHub..." -ForegroundColor Cyan
git diff --cached --quiet
$stagedStatus = $LASTEXITCODE
if ($stagedStatus -eq 1) {
    git commit -m $message
    if ($LASTEXITCODE -ne 0) { throw "Khong tao duoc commit." }
} elseif ($stagedStatus -ne 0) {
    throw "Khong kiem tra duoc thay doi da stage."
}

git push origin main
if ($LASTEXITCODE -ne 0) { throw "Git push that bai." }

Write-Host "HOAN TAT! Da day len GitHub thanh cong voi thong diep: '$message'" -ForegroundColor Green
