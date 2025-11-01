# 🐛 任务名称显示问题修复报告

## 📋 问题描述

**用户反馈：**
> "为什么现在界面显示的任务名没考试名称，而且侧边栏的任务名称显示也错误"

## 🔍 问题分析

### 根本原因

在 `src/api/file_utils.py` 的 `get_all_jobs()` 函数中，存在以下问题：

1. **字段名错误**：读取 `exam_config.json` 时使用了错误的字段名
   - ❌ 错误：`config_data.get("exam_name", "")`
   - ✅ 正确：`config_data.get("exam_title", "")`

2. **未优先读取 status.json**：应该优先从 `status.json` 读取完整的任务信息，而不是重新构建

3. **缺少 status 字段**：没有 `status.json` 时未提供 status 字段

### 问题影响

- ❌ 所有任务的考试名称显示为空
- ❌ 侧边栏任务列表显示不完整
- ❌ 下拉框任务选择显示异常

## 🔧 修复方案

### 修改文件
`src/api/file_utils.py` - `get_all_jobs()` 函数

### 修改内容

#### 1. 优先读取 status.json
```python
# 优先尝试从 status.json 读取完整信息
status_file = job_dir / "status.json"
if status_file.exists():
    try:
        status_data = load_job_status(job_id)
        if status_data:
            jobs.append(status_data)
            continue
    except:
        pass
```

**优点：**
- ✅ 获取完整、准确的任务信息
- ✅ 包含所有必要字段（exam_name, student_count, status, created_at等）
- ✅ 避免重复解析和构建

#### 2. 修正字段名
```python
# 从配置中获取考试名称（注意字段名是 exam_title）
with open(exam_config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)
    # 兼容两种字段名
    exam_name = config_data.get("exam_title", config_data.get("exam_name", ""))
```

**优点：**
- ✅ 使用正确的字段名 `exam_title`
- ✅ 向后兼容 `exam_name`
- ✅ 确保能读取到考试名称

#### 3. 添加默认状态
```python
jobs.append(
    {
        "job_id": job_id,
        "created_at": created_at or job_id,
        "exam_name": exam_name,
        "student_count": student_count,
        "status": "unknown",  # 没有status.json时标记为unknown
    }
)
```

**优点：**
- ✅ 提供完整的数据结构
- ✅ 避免前端访问缺失字段

## ✅ 验证结果

### 测试脚本
运行 `debug_job_data.py` 进行验证：

```bash
uv run python debug_job_data.py
```

### 测试输出
```
📊 返回 1 个任务:

1. Job ID: job_242dc8d3ca78
   考试名称: Python程序设计期中考试  ✅ 正确显示
   学生数量: 10                      ✅ 正确显示
   创建时间: 2025-11-01T11:13:38.287015  ✅ 正确显示
   状态: completed                   ✅ 正确显示

🎨 测试任务名称格式化
1. Python程序设计期中考试 (2025-11-01 11:13:38) [10人]  ✅ 完美
```

### 界面显示

#### ✅ 下拉框任务选择
```
Python程序设计期中考试 (2025-11-01 11:13:38) [10人]
```

#### ✅ 侧边栏任务列表
```
✅ Python程序设计期中考试 (2025-11-01)
   任务ID: job_242dc8d3ca78
   状态: completed
   学生数: 10
   创建时间: 2025-11-01T11:13:38
```

## 📊 修复前后对比

| 项目     | 修复前               | 修复后                   |
| -------- | -------------------- | ------------------------ |
| 考试名称 | ❌ 空白或"未命名考试" | ✅ Python程序设计期中考试 |
| 时间显示 | ⚠️ 仅日期             | ✅ 精确到秒               |
| 学生数量 | ⚠️ 可能不准确         | ✅ 准确                   |
| 状态信息 | ❌ 缺失               | ✅ 完整                   |
| 数据来源 | ❌ 重新构建           | ✅ 从status.json读取      |

## 🎯 技术要点

### 数据流程

#### 修复前（错误流程）
```
get_all_jobs()
  ↓
读取 exam_config.json
  ↓
错误：读取 exam_name 字段（不存在）
  ↓
结果：exam_name = "" (空)
```

#### 修复后（正确流程）
```
get_all_jobs()
  ↓
优先：读取 status.json（完整数据）
  ↓
备用：读取 exam_config.json
  ↓
正确：读取 exam_title 字段
  ↓
结果：完整准确的任务信息
```

### 字段映射

| 文件             | 字段名       | 说明                         |
| ---------------- | ------------ | ---------------------------- |
| exam_config.json | `exam_title` | 考试标题（正确）             |
| status.json      | `exam_name`  | 考试名称（从exam_title复制） |
| API响应          | `exam_name`  | 任务列表中使用               |

## 🚀 后续建议

### 1. 统一字段命名
建议在整个系统中统一使用 `exam_name` 或 `exam_title`，避免混淆。

**建议方案：**
- 配置文件：使用 `exam_title`（更语义化）
- 内部模型：使用 `exam_name`（简洁）
- API响应：使用 `exam_name`（一致性）

### 2. 数据验证
在 `get_all_jobs()` 中添加数据验证，确保返回的数据结构完整。

### 3. 错误处理
改进异常处理，记录详细错误日志，便于调试。

## 📝 相关文件

### 修改的文件
- ✅ `src/api/file_utils.py` - 修复 `get_all_jobs()` 函数

### 测试文件
- 📄 `debug_job_data.py` - 数据验证脚本
- 📄 `test/test_task_name_format.py` - 格式化测试

### 文档
- 📄 `docs/TASK_NAME_FORMAT.md` - 任务名称格式说明
- 📄 `docs/TASK_NAME_OPTIMIZATION_V2.md` - 优化详细文档

## ✅ 总结

### 问题
- ❌ 考试名称不显示
- ❌ 侧边栏信息错误

### 原因
- 🐛 字段名错误（exam_name vs exam_title）
- 🐛 未优先读取 status.json

### 解决
- ✅ 修正字段名
- ✅ 优先读取完整数据
- ✅ 添加兼容处理

### 结果
- ✅ 考试名称正确显示
- ✅ 时间精确到秒
- ✅ 学生数量准确
- ✅ 所有信息完整

---

**修复时间：** 2025-11-01  
**版本：** v2.1  
**状态：** ✅ 已解决
