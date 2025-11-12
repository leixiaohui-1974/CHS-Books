Write-Host "正在启动前端Web系统..." -ForegroundColor Green
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "后端API: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# 检查Node版本
Write-Host "检查Node.js版本..." -ForegroundColor Yellow
node --version
npm --version

Write-Host ""
Write-Host "启动Next.js开发服务器..." -ForegroundColor Yellow

# 启动开发服务器
npm run dev

