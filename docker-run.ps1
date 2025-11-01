#!/usr/bin/env pwsh
# Docker 部署脚本 - PowerShell 版本

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'build', 'dev', 'clean')]
    [string]$Action = 'start'
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 打印标题
function Print-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "============================================" "Cyan"
    Write-ColorOutput "  $Title" "Cyan"
    Write-ColorOutput "============================================" "Cyan"
    Write-Host ""
}

# 检查 Docker 是否安装
function Check-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        Write-ColorOutput "✓ Docker 和 Docker Compose 已安装" "Green"
    }
    catch {
        Write-ColorOutput "✗ 未找到 Docker 或 Docker Compose，请先安装！" "Red"
        Write-ColorOutput "下载地址: https://www.docker.com/products/docker-desktop" "Yellow"
        exit 1
    }
}

# 检查 .env 文件
function Check-Env {
    if (-not (Test-Path ".env")) {
        Write-ColorOutput "⚠ 未找到 .env 文件，从 .env.example 复制..." "Yellow"
        Copy-Item ".env.example" ".env"
        Write-ColorOutput "✓ .env 文件已创建，请配置您的 API 密钥" "Green"
        Write-ColorOutput "编辑文件: .env" "Cyan"
        pause
    }
}

# 主逻辑
Print-Header "🐳 AI智能评分系统 - Docker 部署"

switch ($Action) {
    'start' {
        Write-ColorOutput "🚀 启动服务..." "Green"
        Check-Docker
        Check-Env
        docker-compose up -d
        Write-Host ""
        Write-ColorOutput "✅ 服务启动成功！" "Green"
        Write-ColorOutput "📍 UI 界面: http://localhost:8501" "Cyan"
        Write-ColorOutput "📍 API 文档: http://localhost:8000/docs" "Cyan"
        Write-Host ""
        Write-ColorOutput "查看日志: ./docker-run.ps1 logs" "Yellow"
    }
    
    'stop' {
        Write-ColorOutput "🛑 停止服务..." "Yellow"
        docker-compose down
        Write-ColorOutput "✅ 服务已停止" "Green"
    }
    
    'restart' {
        Write-ColorOutput "🔄 重启服务..." "Yellow"
        docker-compose restart
        Write-ColorOutput "✅ 服务已重启" "Green"
    }
    
    'logs' {
        Write-ColorOutput "📋 查看日志 (Ctrl+C 退出)..." "Cyan"
        docker-compose logs -f
    }
    
    'build' {
        Write-ColorOutput "🔨 重新构建镜像..." "Yellow"
        Check-Docker
        docker-compose build --no-cache
        Write-ColorOutput "✅ 构建完成" "Green"
    }
    
    'dev' {
        Write-ColorOutput "🔧 启动开发环境（支持热重载）..." "Green"
        Check-Docker
        Check-Env
        docker-compose -f docker-compose.dev.yml up
    }
    
    'clean' {
        Write-ColorOutput "🧹 清理 Docker 资源..." "Yellow"
        $response = Read-Host "这将删除所有容器、镜像和卷。确认吗？(y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            docker-compose down -v --rmi all
            Write-ColorOutput "✅ 清理完成" "Green"
        }
        else {
            Write-ColorOutput "已取消" "Yellow"
        }
    }
    
    default {
        Write-ColorOutput "未知命令: $Action" "Red"
        Write-Host ""
        Write-ColorOutput "可用命令:" "Cyan"
        Write-Host "  start   - 启动服务（默认）"
        Write-Host "  stop    - 停止服务"
        Write-Host "  restart - 重启服务"
        Write-Host "  logs    - 查看日志"
        Write-Host "  build   - 重新构建镜像"
        Write-Host "  dev     - 启动开发环境"
        Write-Host "  clean   - 清理所有资源"
        Write-Host ""
        Write-ColorOutput "示例: ./docker-run.ps1 start" "Yellow"
    }
}
