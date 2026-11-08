Write-Host "🛑 Dang dung toan bo he thong Docker..." -ForegroundColor Yellow
docker-compose -f frappe_docker/devcontainer-example/docker-compose.yml stop
Write-Host "💤 He thong da tat an toan. Chuc ban nghi ngoi vui ve!" -ForegroundColor Green
