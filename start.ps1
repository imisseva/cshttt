Write-Host "🟢 1. Dang khoi dong cac container..." -ForegroundColor Cyan
docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml start

Write-Host "🚀 2. Dang khoi dong Web Server ERPNext..." -ForegroundColor Cyan
docker exec -d -w /workspace/development/frappe-bench devcontainer-example-frappe-1 /home/frappe/.local/bin/bench start

Write-Host "✅ He thong da san sang!" -ForegroundColor Green
Write-Host "👉 Hay mo trinh duyet truy cap: http://localhost:8000/app" -ForegroundColor Yellow
