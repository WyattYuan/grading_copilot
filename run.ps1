# AI智能评分系统 - 一键启动脚本
# 同时启动 FastAPI 后端和 Streamlit 前端

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎓 AI智能评分系统 - 一键启动" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# 启动后端 API
Write-Host "`n🚀 启动 FastAPI 后端服务..." -ForegroundColor Yellow
Write-Host "📍 API地址: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "📖 API文档: http://127.0.0.1:8000/docs" -ForegroundColor Gray

$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    uv run python run_api.py
}

# 等待后端启动
Write-Host "`n⏳ 等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动前端 UI
Write-Host "`n🎨 启动 Streamlit 前端界面..." -ForegroundColor Yellow
Write-Host "📍 UI地址: http://localhost:8501" -ForegroundColor Gray

$uiJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    uv run python run_ui.py
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ 服务启动成功!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📍 后端API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "📍 前端界面: http://localhost:8501" -ForegroundColor White
Write-Host "📖 API文档: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n💡 按 Ctrl+C 停止所有服务`n" -ForegroundColor Yellow

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # 检查后台任务状态
        if ($apiJob.State -eq "Failed") {
            Write-Host "❌ 后端服务异常退出" -ForegroundColor Red
            Receive-Job -Job $apiJob
            break
        }
        if ($uiJob.State -eq "Failed") {
            Write-Host "❌ 前端服务异常退出" -ForegroundColor Red
            Receive-Job -Job $uiJob
            break
        }
    }
}
catch {
    Write-Host "`n`n🛑 正在停止服务..." -ForegroundColor Yellow
}
finally {
    # 清理后台任务
    Stop-Job -Job $apiJob, $uiJob -ErrorAction SilentlyContinue
    Remove-Job -Job $apiJob, $uiJob -Force -ErrorAction SilentlyContinue
    Write-Host "✅ 所有服务已停止" -ForegroundColor Green
}
