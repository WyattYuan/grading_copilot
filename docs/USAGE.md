# AI 助教智能评分与分析系统

## 项目简介

这是一个集成了 **人机协同 (Human-in-the-Loop)** 理念的智能评分系统，使用 AI 进行初步评分，人类教师负责监督和微调，确保评分的准确性和一致性。

### 核心特性

- ✅ **AI 自动评分**: 使用 GPT-4 进行智能评分
- ✅ **结构化输出**: 确保评分结果的格式化和可靠性
- ✅ **人工微调**: 教师可以审查和调整 AI 的评分
- ✅ **数据一致性**: 报告与总分表实时同步
- ✅ **批量处理**: 支持一次性处理多个学生的作业
- ✅ **详细报告**: 为每个题目生成详细的评分依据

### 技术栈

- **后端**: FastAPI + Langchain + OpenAI GPT-4
- **前端**: Streamlit
- **数据处理**: Pydantic + Pandas

## 快速开始

### 1. 安装依赖

确保您已安装 Python 3.10 或更高版本。

```bash
# 使用 pip 安装
pip install -e .

# 或使用 uv
uv pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 OpenAI API Key：

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
```

### 3. 启动服务

**方式一: 使用启动脚本 (推荐)**

```bash
# 终端1: 启动后端 API
python run_api.py

# 终端2: 启动前端界面
python run_ui.py
```

**方式二: 手动启动**

```bash
# 终端1: 启动后端
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload

# 终端2: 启动前端
streamlit run src/ui/app.py --server.port 8501
```

### 4. 访问系统

- **前端界面**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs

## 使用指南

### 准备数据

#### 1. 考试配置文件 (exam_config.json)

```json
{
  "exam_title": "计算机科学期中考试",
  "questions": [
    {
      "id": "q1",
      "type": "text",
      "description": "请简述'测试驱动开发(TDD)'的核心三步骤。",
      "max_score": 10,
      "reference_answer": "TDD的核心三步骤是...",
      "scoring_criteria": [
        {
          "points": 4,
          "criterion": "正确描述'红灯'步骤"
        }
      ]
    }
  ]
}
```

#### 2. 学生答案文件

文件名格式: `student_XXX.txt` 或 `student_XXX.docx`

文件内容格式:

```text
[作答: q1]
这是第一题的答案内容...

[作答: q2]
这是第二题的答案内容...
```

#### 3. 打包学生答案

将所有学生答案文件打包成一个 ZIP 文件。

### 使用流程

1. **新建评分任务**
   - 上传考试配置 JSON 文件
   - 上传学生答案 ZIP 文件
   - 点击"开始评分"

2. **查看任务状态**
   - 输入任务 ID
   - 实时查看评分进度
   - 等待任务完成

3. **查看评分结果**
   - 查看总分表
   - 查看统计数据
   - 查看每个学生的详细评分

4. **人工微调**
   - 审查 AI 评分结果
   - 调整不合理的分数
   - 添加调整理由
   - 系统自动同步总分表

## 示例数据

项目提供了示例数据用于测试：

- **考试配置**: `data/examples/exam_config.json`
- **学生答案**: `data/examples/student_1001.txt` 等

您可以直接使用这些示例数据进行测试。

## 项目结构

```
grading-copilot/
├── src/
│   ├── models/          # 数据模型
│   ├── agents/          # Langchain 智能代理
│   ├── api/             # FastAPI 后端
│   └── ui/              # Streamlit 前端
├── data/
│   ├── examples/        # 示例数据
│   ├── uploads/         # 上传文件存储
│   └── reports/         # 评分报告存储
├── run_api.py           # 后端启动脚本
├── run_ui.py            # 前端启动脚本
└── pyproject.toml       # 项目配置
```

## 核心机制

### 数据一致性保证

系统采用 **"报告为源,表格为派生"** 的设计:

1. 每个题目的评分保存为独立的 JSON 报告文件
2. 总分表由所有报告文件动态生成
3. 修改报告后自动重新生成总分表
4. 确保数据始终保持一致

### 评分流程

1. **AI 初评**: Langchain 调用 GPT-4 进行结构化评分
2. **报告生成**: 保存详细的评分依据和分数
3. **总表汇总**: 自动生成总分表
4. **人工审查**: 教师审查并微调
5. **自动同步**: 修改后立即同步总分表

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 API 文档。

主要 API 端点:

- `POST /api/v1/jobs/start` - 启动评分任务
- `GET /api/v1/jobs/{job_id}/status` - 查询任务状态
- `GET /api/v1/jobs/{job_id}/summary` - 获取总分表
- `GET /api/v1/jobs/{job_id}/reports/{student_id}/{question_id}` - 获取评分报告
- `PUT /api/v1/jobs/{job_id}/reports/{student_id}/{question_id}` - 更新评分报告

## 常见问题

### Q: 如何确保 AI 评分的准确性?

A: 系统采用以下措施:
- 使用结构化输出确保评分格式正确
- 明确的评分标准作为 AI 的唯一依据
- 人工审查和微调机制
- 详细的评分依据便于教师判断

### Q: 总分表如何保持同步?

A: 总分表是动态生成的:
- 每次修改报告后自动重新生成总分表
- 总分表从所有报告文件中提取数据
- 不存在手动维护的数据不一致风险

### Q: 支持哪些文件格式?

A: 
- 考试配置: JSON
- 学生答案: TXT, DOCX
- 答案压缩包: ZIP

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!
