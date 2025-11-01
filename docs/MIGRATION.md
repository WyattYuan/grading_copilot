# 数据迁移指南

## 版本更新说明

本次更新添加了学生信息字段（姓名、学号、性别），以下是迁移指南。

## 新增的学生信息字段

系统现在支持以下学生信息：
- **学生姓名** (`student_name`)
- **学号** (`student_id`)
- **性别** (`student_gender`)

## 数据模型变更

### 1. StudentInfo 类（新增）

```python
class StudentInfo(BaseModel):
    """学生信息"""
    student_id: str = Field(description="学生学号")
    student_name: str = Field(description="学生姓名")
    student_gender: str = Field(description="学生性别")
```

### 2. StudentAnswer 类（更新）

**之前：**
```python
class StudentAnswer(BaseModel):
    student_id: str
    answers: dict[str, str]
```

**现在：**
```python
class StudentAnswer(BaseModel):
    student_info: StudentInfo  # 包含姓名、学号、性别
    answers: dict[str, str]
```

### 3. GradingReport 类（更新）

**之前：**
```python
class GradingReport(BaseModel):
    student_id: str
    question_id: str
    # ... 其他字段
```

**现在：**
```python
class GradingReport(BaseModel):
    student_info: StudentInfo  # 包含完整学生信息
    question_id: str
    # ... 其他字段
```

## 学生答案文件格式更新

### 新格式要求

所有学生答案文件（`.txt`、`.docx` 或 `.md`）必须在开头包含学生信息：

```
学生姓名: 张三
学号: 1001
性别: 男

[作答: q1]
第一题的答案...

[作答: q2]
第二题的答案...
```

### 旧格式（仅供参考，不再支持）

```
[作答: q1]
第一题的答案...

[作答: q2]
第二题的答案...
```

## 总分表格式更新

### 新的 CSV 格式

总分表现在包含学生信息列：

| student_id | student_name | student_gender | q1_score | q2_score | q3_score | total_score |
|------------|--------------|----------------|----------|----------|----------|-------------|
| 1001       | 张三         | 男             | 8.0      | 15.0     | 11.0     | 34.0        |
| 1002       | 李四         | 女             | 10.0     | 15.0     | 12.0     | 37.0        |
| 1003       | 王五         | 男             | 2.0      | 13.0     | 9.0      | 24.0        |

## 如何迁移现有数据

### 步骤 1: 更新学生答案文件

在每个学生答案文件的开头添加学生信息：

```bash
# 示例：修改 student_1001.txt
```

**修改前：**
```
[作答: q1]
答案内容...
```

**修改后：**
```
学生姓名: 张三
学号: 1001
性别: 男

[作答: q1]
答案内容...
```

### 步骤 2: 重新创建 ZIP 文件

```bash
cd data/examples
python ../../create_example_zip.py
```

### 步骤 3: 重新运行评分任务

由于数据模型已更新，建议重新运行评分任务以生成新格式的报告。

## 向后兼容性

系统提供了基本的向后兼容：
- 如果学生答案文件中缺少学生信息，系统会使用默认值：
  - `student_id`: 从文件名提取
  - `student_name`: "未填写"
  - `student_gender`: "未填写"

## UI 界面更新

### 学生详情页面

现在会显示完整的学生信息：
- 姓名
- 学号
- 性别
- 总分

### 总分表

包含学生姓名和性别列，便于识别和统计。

## 常见问题

### Q: 旧的报告数据会怎样？

A: 旧的报告数据格式不兼容，建议使用新格式重新运行评分任务。

### Q: 如果学生没有填写姓名怎么办？

A: 系统会自动使用"未填写"作为默认值，不会影响评分流程。

### Q: 性别字段必须填写吗？

A: 建议填写，但不是强制的。可以填写"男"、"女"或其他值。

## 示例文件

参考以下示例文件：
- `data/examples/学生作答模板.md` - 通用模板
- `data/examples/student_1001.txt` - 示例学生答案
- `data/examples/student_1002.txt` - 示例学生答案
- `data/examples/student_1003.txt` - 示例学生答案
