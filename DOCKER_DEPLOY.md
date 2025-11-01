# 🐳 Docker 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [部署步骤](#部署步骤)
- [常用命令](#常用命令)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

---

## 🚀 快速开始

### 一键部署（推荐）

```powershell
# 1. 启动服务
./docker-run.ps1 start

# 2. 访问应用
# UI: http://localhost:8501
# API: http://localhost:8000/docs
```

---

## 📦 环境要求

### 必需软件

- **Docker Desktop** >= 20.10
- **Docker Compose** >= 2.0

### 下载地址

- Windows: https://www.docker.com/products/docker-desktop
- Mac: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

---

## 📝 部署步骤

### 方式一：使用脚本（推荐）

#### Windows (PowerShell)

```powershell
# 1. 启动服务
./docker-run.ps1 start

# 2. 查看日志
./docker-run.ps1 logs

# 3. 停止服务
./docker-run.ps1 stop
```

#### 查看所有命令

```powershell
./docker-run.ps1 help
```

可用命令：
- `start` - 启动服务
- `stop` - 停止服务
- `restart` - 重启服务
- `logs` - 查看日志
- `build` - 重新构建镜像
- `dev` - 启动开发环境（热重载）
- `clean` - 清理所有资源

---

### 方式二：手动部署

#### 1. 检查环境

```powershell
# 检查 Docker 版本
docker --version
docker-compose --version
```

#### 2. 配置环境变量

```powershell
# 复制环境变量文件
Copy-Item .env.example .env

# 编辑 .env 文件，配置 API 密钥
notepad .env
```

必须配置的环境变量：
```env
# OpenAI API（如果使用 OpenAI）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 或者使用阿里云通义千问
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

#### 3. 构建镜像

```powershell
# 构建所有服务
docker-compose build

# 或单独构建某个服务
docker-compose build api
docker-compose build ui
```

#### 4. 启动服务

```powershell
# 后台启动
docker-compose up -d

# 前台启动（可查看日志）
docker-compose up
```

#### 5. 验证服务

```powershell
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问：
- **UI 界面**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs

---

## 🔧 常用命令

### 服务管理

```powershell
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart api
docker-compose restart ui
```

### 日志查看

```powershell
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f ui

# 查看最后 100 行
docker-compose logs --tail=100 api
```

### 镜像管理

```powershell
# 重新构建（不使用缓存）
docker-compose build --no-cache

# 查看镜像
docker images | Select-String "grading"

# 删除镜像
docker-compose down --rmi all
```

### 容器管理

```powershell
# 进入容器
docker exec -it grading_api bash
docker exec -it grading_ui bash

# 查看容器资源使用
docker stats grading_api grading_ui

# 清理停止的容器
docker container prune
```

### 数据卷管理

```powershell
# 查看数据卷
docker volume ls

# 清理未使用的卷
docker volume prune

# 备份数据
docker cp grading_api:/app/data ./backup/data
```

---

## ⚙️ 配置说明

### docker-compose.yml 关键配置

#### 端口映射

```yaml
ports:
  - "8000:8000"  # API 服务
  - "8501:8501"  # UI 服务
```

修改宿主机端口：
```yaml
ports:
  - "9000:8000"  # 将 API 映射到 9000 端口
  - "9501:8501"  # 将 UI 映射到 9501 端口
```

#### 数据持久化

```yaml
volumes:
  - ./data:/app/data        # 数据目录
  - ./.env:/app/.env        # 环境变量
```

#### 资源限制

添加资源限制（可选）：
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

---

## 🔍 故障排查

### 问题 1: 端口被占用

**错误信息**:
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解决方案**:
```powershell
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 使用其他端口
```

---

### 问题 2: 容器启动失败

**排查步骤**:
```powershell
# 1. 查看容器状态
docker-compose ps

# 2. 查看详细日志
docker-compose logs api
docker-compose logs ui

# 3. 检查容器
docker inspect grading_api
```

---

### 问题 3: 网络连接问题

**UI 无法连接 API**:

检查 `.env` 文件中的配置：
```env
# 确保使用服务名而非 localhost
API_HOST=api  # 正确
# API_HOST=localhost  # 错误
```

---

### 问题 4: 权限问题

**Linux/Mac 上的权限问题**:
```bash
# 修改数据目录权限
chmod -R 777 data/
```

---

### 问题 5: 镜像构建失败

```powershell
# 清理缓存重新构建
docker-compose build --no-cache

# 检查 Dockerfile 语法
docker-compose config
```

---

## 🌐 生产环境部署

### 使用 Nginx 反向代理

#### nginx.conf 示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # UI 服务
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # API 服务
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### 使用 HTTPS

#### 1. 获取 SSL 证书（使用 Let's Encrypt）

```bash
certbot --nginx -d your-domain.com
```

#### 2. 修改 nginx.conf

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... 其他配置
}
```

---

## 📊 性能优化

### 1. 使用多阶段构建

在 Dockerfile 中使用多阶段构建减小镜像体积：

```dockerfile
# 构建阶段
FROM python:3.11 as builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --user -e .

# 运行阶段
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
# ...
```

### 2. 配置日志轮转

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 使用健康检查

已在 `docker-compose.yml` 中配置：
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 🔐 安全建议

1. **不要将 `.env` 文件提交到版本控制**
   ```bash
   # 已在 .gitignore 中
   .env
   ```

2. **使用环境变量管理密钥**
   - 生产环境使用 Docker secrets 或 Vault

3. **限制容器权限**
   ```yaml
   services:
     api:
       user: "1000:1000"  # 非 root 用户
       read_only: true     # 只读文件系统
   ```

4. **定期更新基础镜像**
   ```powershell
   docker-compose pull
   docker-compose build
   ```

---

## 📚 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Streamlit Docker 部署](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
- [FastAPI Docker 部署](https://fastapi.tiangolo.com/deployment/docker/)

---

## 🆘 获取帮助

遇到问题？

1. 查看日志: `./docker-run.ps1 logs`
2. 检查配置: `docker-compose config`
3. 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)

---

**祝部署顺利！🎉**
