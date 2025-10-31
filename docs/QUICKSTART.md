# AI 助教智能评分系统 - 快速开始指南

## 📋 前置要求

- Python 3.10 或更高版本
- OpenAI API Key

## 🚀 快速启动

### 1. 安装依赖

```powershell
# 使用 uv (推荐)
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

创建 `.env` 文件:

```powershell
Copy-Item .env.example .env
```

编辑 `.env` 文件,填入您的 OpenAI API Key:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
```

### 3. 启动服务

**打开两个终端:**

终端 1 - 启动后端:
```powershell
uv run python run_api.py
```

终端 2 - 启动前端:
```powershell
uv run python run_ui.py
```

### 4. 访问系统

浏览器访问:
- **前端界面**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs

## 🧪 使用示例数据测试

系统已准备好示例数据,您可以直接测试:

1. 在前端界面选择"新建评分任务"
2. 上传文件:
   - **考试配置**: `data/examples/exam_config.json`
   - **学生答案**: `data/examples/student_answers.zip`
3. 点击"开始评分"
4. 前往"查看任务状态"监控进度
5. 完成后在"查看评分结果"查看结果
6. 在"人工微调"页面调整评分

## 📁 项目结构

```
grading-copilot/
├── src/
│   ├── models/schemas.py      # 数据模型
│   ├── agents/grading_agent.py # AI评分代理
│   ├── api/
│   │   ├── main.py            # FastAPI主应用
│   │   ├── file_utils.py      # 文件处理工具
│   │   └── sync_manager.py    # 数据同步管理
│   └── ui/app.py              # Streamlit界面
├── data/
│   └── examples/              # 示例数据
├── run_api.py                 # 后端启动脚本
└── run_ui.py                  # 前端启动脚本
```

## 🔧 常用命令

```powershell
# 创建示例ZIP包
uv run python create_example_zip.py

# 仅启动后端
uv run python run_api.py

# 仅启动前端
uv run python run_ui.py
```

## 📖 详细文档

请查看 `docs/USAGE.md` 获取完整使用指南。

## ❓ 问题排查

### API 无法连接

确保后端服务已启动,检查 http://localhost:8000 是否可访问。

### OpenAI API 错误

1. 检查 `.env` 文件中的 API Key 是否正确
2. 确保 API Key 有足够的额度
3. 检查网络连接

### 文件解析错误

确保学生答案文件格式正确:
```
[作答: q1]
答案内容...

[作答: q2]
答案内容...
```

## 🎯 下一步

- 准备您自己的考试配置文件
- 收集学生答案并打包成ZIP
- 开始使用系统进行智能评分!
