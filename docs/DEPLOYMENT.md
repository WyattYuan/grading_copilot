# 📦 应用打包与发布指南

## 🎯 发布方案概览

根据不同的使用场景，我们提供以下几种打包发布方案：

| 方案                 | 适用场景         | 优点                  | 缺点             |
| -------------------- | ---------------- | --------------------- | ---------------- |
| **Docker 容器化**    | 生产环境、云部署 | 环境一致、易部署      | 需要 Docker 知识 |
| **PyInstaller 打包** | Windows 桌面应用 | 双击运行、无需 Python | 包体积大         |
| **云平台部署**       | 在线服务         | 易访问、自动扩展      | 持续成本         |
| **源码发布**         | 开发者           | 灵活、可定制          | 需要配置环境     |

---

## 🐳 方案1: Docker 容器化（推荐）

### 优势
- ✅ 环境完全隔离，"一次构建，到处运行"
- ✅ 包含所有依赖，无需手动安装
- ✅ 易于部署到云平台（阿里云、AWS、Azure等）
- ✅ 适合生产环境

### 步骤

#### 1. 创建 Dockerfile

**API 服务 Dockerfile:**

```dockerfile
# Dockerfile.api
FROM python:3.11-slim

WORKDIR /app

# 安装 uv（快速 Python 包管理器）
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY data/ ./data/
COPY .env.example ./.env

# 安装依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**UI 服务 Dockerfile:**

```dockerfile
# Dockerfile.ui
FROM python:3.11-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY .env.example ./.env

# 安装依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["uv", "run", "streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: grading_api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped

  ui:
    build:
      context: .
      dockerfile: Dockerfile.ui
    container_name: grading_ui
    ports:
      - "8501:8501"
    volumes:
      - ./.env:/app/.env
    environment:
      - API_HOST=api
      - API_PORT=8000
    depends_on:
      - api
    restart: unless-stopped

volumes:
  data:
```

#### 3. 构建和运行

```powershell
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 访问应用
# UI: http://localhost:8501
# API: http://localhost:8000/docs
```

#### 4. 发布到 Docker Hub

```powershell
# 登录 Docker Hub
docker login

# 打标签
docker tag grading_copilot-api:latest your-username/grading-copilot-api:v1.0
docker tag grading_copilot-ui:latest your-username/grading-copilot-ui:v1.0

# 推送镜像
docker push your-username/grading-copilot-api:v1.0
docker push your-username/grading-copilot-ui:v1.0
```

---

## 💻 方案2: PyInstaller 打包（Windows 桌面应用）

### 优势
- ✅ 生成独立的 .exe 文件
- ✅ 用户无需安装 Python 环境
- ✅ 双击即可运行

### 缺点
- ⚠️ 包体积较大（500MB+）
- ⚠️ 首次启动较慢
- ⚠️ Streamlit 打包复杂

### 步骤

#### 1. 安装 PyInstaller

```powershell
uv pip install pyinstaller
```

#### 2. 创建启动脚本

**launcher.py** (统一启动器):

```python
"""
AI智能评分系统 - 统一启动器
"""
import subprocess
import time
import webbrowser
import sys
from pathlib import Path

def start_api():
    """启动 API 服务"""
    print("🚀 正在启动 API 服务...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", 
         "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return api_process

def start_ui():
    """启动 UI 服务"""
    print("🎨 正在启动用户界面...")
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "src/ui/app.py",
         "--server.port", "8501",
         "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return ui_process

def main():
    print("="*60)
    print("🎓 AI智能评分系统".center(60))
    print("="*60)
    
    # 启动服务
    api_proc = start_api()
    time.sleep(3)  # 等待 API 启动
    
    ui_proc = start_ui()
    time.sleep(5)  # 等待 UI 启动
    
    # 打开浏览器
    print("🌐 正在打开浏览器...")
    webbrowser.open("http://localhost:8501")
    
    print("\n✅ 系统已启动！")
    print("📍 UI 地址: http://localhost:8501")
    print("📍 API 地址: http://localhost:8000/docs")
    print("\n⚠️  关闭此窗口将停止所有服务")
    print("="*60)
    
    try:
        # 保持运行
        api_proc.wait()
        ui_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        api_proc.terminate()
        ui_proc.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
```

#### 3. 创建 PyInstaller 配置

**launcher.spec**:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('data/examples', 'data/examples'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'streamlit',
        'fastapi',
        'langchain',
        'langchain_openai',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI智能评分系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 如果有图标
)
```

#### 4. 打包

```powershell
# 使用 spec 文件打包
pyinstaller launcher.spec

# 或使用命令行（简化版）
pyinstaller --onefile --name "AI智能评分系统" --add-data "src;src" --add-data "data/examples;data/examples" launcher.py
```

#### 5. 测试和分发

```powershell
# 打包后的文件在 dist/ 目录
cd dist
.\AI智能评分系统.exe

# 创建发布包
# 1. 将 dist/AI智能评分系统.exe 放入文件夹
# 2. 添加 .env.example 并重命名为 .env
# 3. 添加 README.txt 使用说明
# 4. 压缩为 .zip 文件发布
```

**注意事项:**
- PyInstaller 打包 Streamlit 应用较复杂，可能需要额外配置
- 建议使用 Docker 方案或源码方案

---

## ☁️ 方案3: 云平台部署

### 3.1 部署到 Streamlit Cloud (免费)

**优势:**
- ✅ 完全免费（有限制）
- ✅ 自动部署、自动更新
- ✅ 提供公网访问

**步骤:**

1. **推送代码到 GitHub**
   ```powershell
   git add .
   git commit -m "准备部署"
   git push origin main
   ```

2. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 使用 GitHub 账号登录
   - 点击 "New app"

3. **配置部署**
   - Repository: 选择你的仓库
   - Branch: main
   - Main file path: `src/ui/app.py`
   - Advanced settings: 添加环境变量（API keys等）

4. **注意事项**
   - API 服务需要单独部署（可用 Railway、Render 等）
   - 修改 `src/config.py` 中的 API_HOST 为实际部署的 API 地址

### 3.2 部署到 Railway (推荐)

**优势:**
- ✅ 支持 Docker 和源码部署
- ✅ 自动 HTTPS
- ✅ 每月免费额度

**步骤:**

1. **在项目根目录创建 railway.json**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.api"
  },
  "deploy": {
    "startCommand": "uv run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

2. **部署**
   - 访问 https://railway.app/
   - 连接 GitHub 仓库
   - 选择 "Deploy from GitHub repo"
   - 添加环境变量
   - 点击 Deploy

3. **配置 UI 连接 API**
   - 获取 API 的公网地址（如 `https://xxx.railway.app`）
   - 在 UI 部署时设置环境变量 `API_HOST`

### 3.3 部署到阿里云/腾讯云

**使用云服务器 (ECS):**

```bash
# 1. SSH 登录服务器
ssh user@your-server-ip

# 2. 安装 Docker 和 Docker Compose
# (具体步骤见各云平台文档)

# 3. 克隆代码
git clone https://github.com/your-username/grading_copilot.git
cd grading_copilot

# 4. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 5. 启动服务
docker-compose up -d

# 6. 配置防火墙（开放 8000 和 8501 端口）
# 7. 配置域名和反向代理（Nginx）
```

---

## 📄 方案4: 源码发布

### 优势
- ✅ 最灵活
- ✅ 用户可自定义
- ✅ 适合开发者

### 发布包结构

```
grading_copilot-v1.0.0/
├── src/                    # 源代码
├── data/
│   └── examples/          # 示例数据
├── docs/                  # 文档
├── pyproject.toml         # 依赖配置
├── uv.lock               # 锁定文件
├── .env.example          # 环境变量模板
├── README.md             # 使用说明
├── run_api.py            # API 启动脚本
├── run_ui.py             # UI 启动脚本
└── install.bat           # Windows 安装脚本（可选）
```

### 创建安装脚本

**install.bat** (Windows):

```batch
@echo off
echo ================================
echo AI智能评分系统 - 安装向导
echo ================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [2/4] 安装 UV 包管理器...
pip install uv
if errorlevel 1 (
    echo 错误: UV 安装失败
    pause
    exit /b 1
)

echo [3/4] 安装项目依赖...
uv sync
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo [4/4] 配置环境变量...
if not exist .env (
    copy .env.example .env
    echo 已创建 .env 文件，请编辑配置 API Key
)

echo.
echo ================================
echo 安装完成！
echo ================================
echo.
echo 使用方法:
echo 1. 编辑 .env 文件，填写 OPENAI_API_KEY
echo 2. 双击 start.bat 启动系统
echo.
pause
```

**start.bat** (启动脚本):

```batch
@echo off
title AI智能评分系统

echo ================================
echo 正在启动系统...
echo ================================

start "API Server" cmd /k "uv run python run_api.py"
timeout /t 3 /nobreak > nul

start "UI Server" cmd /k "uv run python run_ui.py"
timeout /t 5 /nobreak > nul

start http://localhost:8501

echo.
echo ================================
echo 系统已启动！
echo ================================
echo UI: http://localhost:8501
echo API: http://localhost:8000/docs
echo.
echo 关闭命令窗口将停止服务
echo ================================
pause
```

**install.sh** (Linux/Mac):

```bash
#!/bin/bash

echo "================================"
echo "AI智能评分系统 - 安装向导"
echo "================================"
echo

echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3，请先安装"
    exit 1
fi
python3 --version

echo "[2/4] 安装 UV 包管理器..."
pip3 install uv

echo "[3/4] 安装项目依赖..."
uv sync

echo "[4/4] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建 .env 文件，请编辑配置 API Key"
fi

echo
echo "================================"
echo "安装完成！"
echo "================================"
echo
echo "使用方法:"
echo "1. 编辑 .env 文件，填写 OPENAI_API_KEY"
echo "2. 运行 ./start.sh 启动系统"
echo
```

### 发布步骤

```powershell
# 1. 创建发布目录
mkdir release
cd release

# 2. 复制必要文件
Copy-Item -Recurse ..\src .\
Copy-Item -Recurse ..\data\examples .\data\examples
Copy-Item -Recurse ..\docs .\
Copy-Item ..\pyproject.toml .\
Copy-Item ..\uv.lock .\
Copy-Item ..\README.md .\
Copy-Item ..\.env.example .\
Copy-Item ..\run_api.py .\
Copy-Item ..\run_ui.py .\

# 3. 添加安装脚本
# (将上面的 install.bat 和 start.bat 放入)

# 4. 创建压缩包
Compress-Archive -Path .\* -DestinationPath ..\grading_copilot-v1.0.0.zip

# 5. 上传到 GitHub Releases
# 访问 https://github.com/your-repo/releases/new
```

---

## 🎯 推荐方案对比

### 场景1: 内网部署（学校、企业）
**推荐: Docker 容器化**
- 使用 `docker-compose.yml` 一键部署
- 易于维护和更新
- 环境隔离，不影响其他系统

### 场景2: 公开在线服务
**推荐: 云平台部署（Railway/阿里云）**
- Railway: 适合小规模、快速部署
- 阿里云/腾讯云: 适合大规模、高性能需求

### 场景3: 给非技术用户使用
**推荐: 源码 + 安装脚本**
- 提供详细的图文安装教程
- 包含一键安装脚本
- 附带示例数据

### 场景4: 本地快速试用
**推荐: Docker 或源码**
- Docker: `docker-compose up -d`
- 源码: `install.bat` + `start.bat`

---

## 📋 发布前检查清单

### 代码准备
- [ ] 移除调试代码和日志
- [ ] 更新版本号（`pyproject.toml`）
- [ ] 完善 README.md
- [ ] 添加 LICENSE 文件
- [ ] 测试所有功能

### 安全检查
- [ ] .env 文件不包含在发布包中
- [ ] 提供 .env.example 模板
- [ ] API Key 等敏感信息通过环境变量配置
- [ ] 添加 .gitignore

### 文档准备
- [ ] 安装指南
- [ ] 使用教程
- [ ] API 文档
- [ ] 常见问题 FAQ
- [ ] 更新日志 CHANGELOG

### 测试
- [ ] 本地环境测试
- [ ] 全新环境安装测试
- [ ] Docker 构建测试
- [ ] 跨平台测试（Windows/Linux/Mac）

---

## 🚀 快速开始（发布后的用户视角）

### Docker 方式

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/grading_copilot.git
cd grading_copilot

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 API Key

# 3. 启动
docker-compose up -d

# 4. 访问
# UI: http://localhost:8501
# API: http://localhost:8000/docs
```

### 源码方式 (Windows)

```powershell
# 1. 下载并解压
# 2. 双击 install.bat 安装
# 3. 编辑 .env 文件
# 4. 双击 start.bat 启动
# 5. 浏览器自动打开
```

---

## 💡 最佳实践

### 1. 版本管理
- 使用语义化版本号（如 v1.0.0）
- 维护 CHANGELOG.md
- 打 Git 标签

### 2. 持续集成/部署（CI/CD）
使用 GitHub Actions 自动化：

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -f Dockerfile.api -t grading-api:${{ github.ref_name }} .
          docker build -f Dockerfile.ui -t grading-ui:${{ github.ref_name }} .
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            grading_copilot-${{ github.ref_name }}.zip
```

### 3. 监控和日志
- 添加健康检查端点
- 使用结构化日志
- 配置错误追踪（如 Sentry）

---

## 📞 获取帮助

- 📖 [完整文档](docs/)
- 🐛 [问题反馈](https://github.com/your-repo/issues)
- 💬 [讨论区](https://github.com/your-repo/discussions)

---

**版本:** v1.0.0  
**最后更新:** 2025年11月1日
