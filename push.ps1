param(
    [string]$message = "update customizations and doctypes"
)

Write-Host "📦 1. Dang thu thap cac Custom DocType va Customizations..." -ForegroundColor Cyan

# Tao thu muc luu tru neu chua co
New-Item -ItemType Directory -Force -Path custom_doctypes\custom | Out-Null

# 1. Gom DocType Level Transfer Request
$doctypeSource = "frappe_docker\development\frappe-bench\apps\education\education\education\doctype"
if (Test-Path "$doctypeSource\level_transfer_request") {
    New-Item -ItemType Directory -Force -Path custom_doctypes\level_transfer_request | Out-Null
    Copy-Item -Recurse -Force "$doctypeSource\level_transfer_request\*" custom_doctypes\level_transfer_request\
    Remove-Item -Recurse -Force custom_doctypes\level_transfer_request\__pycache__ -ErrorAction SilentlyContinue
}

# 2. Gom bat ky file Customization nao duoc export (vi du: room.json, student.json)
$customSource = "frappe_docker\development\frappe-bench\apps\education\education\education\custom"
if (Test-Path $customSource) {
    Copy-Item -Recurse -Force "$customSource\*" custom_doctypes\custom\
}

Write-Host "🚀 2. Dang day len GitHub..." -ForegroundColor Cyan
git add custom_doctypes README.md push.ps1 pull.ps1
git commit -m $message
git push origin main

Write-Host "✅ Da day len GitHub thanh cong!" -ForegroundColor Green
