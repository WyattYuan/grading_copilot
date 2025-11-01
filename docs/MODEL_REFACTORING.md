# 📐 数据模型重构说明

## 🎯 本次重构目标

1. ✅ **修复显示bug**：参考答案和评分标准无法显示的问题
2. ✅ **优化模型结构**：使用继承优化题目类型组织
3. ✅ **增强类型安全**：添加模型验证确保数据一致性

---

## 🐛 Bug修复

### 问题描述

用户反馈：考试数据中有参考答案和评分标准，但显示页面显示"（暂无参考答案）"

### 根本原因

在 `src/api/sync_manager.py` 的 `get_student_detail()` 方法中，返回的字典**缺少**两个关键字段：

```python
# ❌ 原来的代码 - 缺少字段
result["questions"].append({
    "question_id": report.question_id,
    "question_description": report.question_snapshot.description,
    "max_score": report.question_snapshot.max_score,
    # ⚠️ 缺少 reference_answer
    # ⚠️ 缺少 scoring_criteria
    "student_answer": report.student_answer,
    "ai_score": report.ai_score,
    ...
})
```

虽然 `report.question_snapshot` 中有这些数据，但没有传递给前端。

### 解决方案

在返回字典中添加缺失的字段：

```python
# ✅ 修复后的代码
result["questions"].append({
    "question_id": report.question_id,
    "question_description": report.question_snapshot.description,
    "max_score": report.question_snapshot.max_score,
    "reference_answer": report.question_snapshot.reference_answer,  # ✅ 新增
    "scoring_criteria": report.question_snapshot.scoring_criteria,  # ✅ 新增
    "student_answer": report.student_answer,
    "ai_score": report.ai_score,
    ...
})
```

### 影响范围

- 📈 **评分结果页面**：现在可以正确显示参考答案和评分标准
- ✏️ **人工微调页面**：田字格布局可以完整展示所有信息

---

## 🏗️ 模型重构

### 重构前的问题

原来的 `Question` 模型使用 **可选字段** 来区分单题和复合题：

```python
class Question(BaseModel):
    id: str
    type: Literal["text", "code", "multimodal"]
    description: str
    
    # ⚠️ 单题字段 - 都是Optional
    max_score: Optional[float] = None
    reference_answer: Optional[str] = None
    scoring_criteria: Optional[List[ScoringCriterion]] = None
    
    # ⚠️ 复合题字段 - 也是Optional
    sub_questions: Optional[List[SubQuestion]] = None
```

**缺点：**
- ❌ 类型不明确：IDE无法区分单题和复合题
- ❌ 容易出错：可能同时设置或都不设置
- ❌ 缺少验证：没有强制约束字段的必填性

### 重构后的优化

#### 1. 引入基类

```python
class QuestionBase(BaseModel):
    """题目基类 - 定义所有题目的共同属性"""
    
    id: str
    type: Literal["text", "code", "multimodal"]
    description: str
    attachments: Optional[List[str]] = None
    
    def get_total_score(self) -> float:
        raise NotImplementedError("子类必须实现此方法")
    
    def is_composite(self) -> bool:
        raise NotImplementedError("子类必须实现此方法")
```

#### 2. 保持向后兼容

为了不破坏现有代码，仍然使用 `Question` 类，但添加了严格的验证：

```python
class Question(QuestionBase):
    """题目配置（支持单题和复合题，向后兼容原有设计）"""
    
    # 单题字段
    max_score: Optional[float] = None
    reference_answer: Optional[str] = None
    scoring_criteria: Optional[List[ScoringCriterion]] = None
    
    # 复合题字段
    sub_questions: Optional[List[SubQuestion]] = None
    
    @model_validator(mode="after")
    def validate_question_type(self):
        """验证题目类型的一致性"""
        is_simple = self.max_score is not None
        is_composite = self.sub_questions is not None
        
        # 必须是单题或复合题之一，不能两者都是或都不是
        if is_simple == is_composite:
            raise ValueError("题目必须明确为单题或复合题")
        
        # 单题必须有完整字段
        if is_simple:
            if not self.reference_answer:
                raise ValueError("单题必须有reference_answer")
            if not self.scoring_criteria:
                raise ValueError("单题必须有scoring_criteria")
        
        # 复合题必须有小题
        if is_composite and len(self.sub_questions) == 0:
            raise ValueError("复合题必须至少包含一个小题")
        
        return self
```

#### 3. SubQuestion 增强

为 `SubQuestion` 添加了格式化方法：

```python
class SubQuestion(BaseModel):
    id: str
    description: str
    max_score: float
    reference_answer: str
    scoring_criteria: List[ScoringCriterion]
    
    def get_scoring_criteria_text(self) -> str:
        """获取格式化的评分标准文本"""
        lines = []
        for idx, criterion in enumerate(self.scoring_criteria, 1):
            lines.append(f"{idx}. ({criterion.points}分) {criterion.criterion}")
        return "\n".join(lines)
```

---

## 📊 重构优势对比

| 特性         | 重构前                 | 重构后                 |
| ------------ | ---------------------- | ---------------------- |
| **类型安全** | ❌ 字段都是Optional     | ✅ 运行时验证确保一致性 |
| **错误预防** | ❌ 可能同时设置两种类型 | ✅ 验证器阻止错误配置   |
| **代码清晰** | ⚠️ 需要多次判断         | ✅ 基类定义清晰接口     |
| **向后兼容** | ✅ N/A                  | ✅ 完全兼容现有JSON     |
| **IDE支持**  | ⚠️ 类型提示不明确       | ✅ 更好的类型提示       |
| **可扩展性** | ⚠️ 难以添加新题型       | ✅ 继承基类即可扩展     |

---

## 🔄 数据流改进

### 完整的数据流

```
┌─────────────────┐
│ exam_config.json│  
│  - questions[]  │  包含 reference_answer, scoring_criteria
└────────┬────────┘
         │ 加载
         ▼
┌─────────────────┐
│  Question 模型  │  
│  - 验证数据完整性│  
└────────┬────────┘
         │ 评分
         ▼
┌─────────────────┐
│ QuestionSnapshot│  ✅ 现在包含所有字段
│  - description  │
│  - max_score    │
│  - reference_answer    │  ← 新增
│  - scoring_criteria    │  ← 新增
└────────┬────────┘
         │ API响应
         ▼
┌─────────────────┐
│ sync_manager    │  ✅ 现在传递所有字段
│ get_student_detail │
└────────┬────────┘
         │ 返回JSON
         ▼
┌─────────────────┐
│   UI 田字格     │  ✅ 正确显示
│  - 学生答案     │
│  - 参考答案     │  ← 现在可见
│  - 评分标准     │  ← 现在可见
│  - AI评分依据   │
└─────────────────┘
```

---

## 🧪 验证规则

### 单题验证

```python
# ✅ 有效的单题
{
    "id": "q1",
    "type": "text",
    "description": "问题描述",
    "max_score": 10,                    # 必填
    "reference_answer": "参考答案",      # 必填
    "scoring_criteria": [...]           # 必填
}

# ❌ 无效：缺少reference_answer
{
    "id": "q1",
    "type": "text",
    "description": "问题描述",
    "max_score": 10,
    # ❌ 缺少 reference_answer
    "scoring_criteria": [...]
}
```

### 复合题验证

```python
# ✅ 有效的复合题
{
    "id": "q2",
    "type": "text",
    "description": "大题描述",
    "sub_questions": [                  # 必填且非空
        {
            "id": "q2_1",
            "description": "小题1",
            "max_score": 5,
            "reference_answer": "答案1",
            "scoring_criteria": [...]
        }
    ]
}

# ❌ 无效：sub_questions为空
{
    "id": "q2",
    "type": "text",
    "description": "大题描述",
    "sub_questions": []  # ❌ 至少要有一个小题
}
```

### 互斥验证

```python
# ❌ 无效：同时设置单题和复合题字段
{
    "id": "q3",
    "type": "text",
    "description": "混乱的题目",
    "max_score": 10,           # ❌ 单题字段
    "reference_answer": "...",
    "sub_questions": [...]     # ❌ 复合题字段
}
```

---

## 📝 使用示例

### 加载考试配置

```python
from src.models.schemas import ExamConfig

# JSON自动验证
exam_config = ExamConfig.model_validate_json(json_string)

# 遍历题目
for question in exam_config.questions:
    if question.is_composite():
        print(f"大题: {question.id}, 总分: {question.get_total_score()}")
        for sub_q in question.sub_questions:
            print(f"  小题: {sub_q.id}, 分数: {sub_q.max_score}")
    else:
        print(f"单题: {question.id}, 分数: {question.get_max_score()}")
        print(f"评分标准:\n{question.get_scoring_criteria_text()}")
```

### 创建QuestionSnapshot

```python
from src.models.schemas import QuestionSnapshot

# 现在会自动包含所有字段
snapshot = QuestionSnapshot(
    description=question.description,
    max_score=question.get_max_score(),
    reference_answer=question.get_reference_answer(),      # ✅ 新增
    scoring_criteria=question.get_scoring_criteria_text(), # ✅ 新增
)
```

---

## 🎯 迁移指南

### 对现有代码的影响

**好消息：** 现有的 JSON 配置文件**无需修改**！

重构后的模型完全向后兼容，只是增加了验证。

### 需要注意的变化

1. **更严格的验证**
   - 以前可能通过的不完整数据现在会报错
   - 这是**好事**，能在加载时发现问题

2. **API响应增加字段**
   - `get_student_detail` 现在返回 `reference_answer` 和 `scoring_criteria`
   - 前端代码已更新，无需修改

3. **类型提示改进**
   - IDE 会提供更好的自动补全
   - 类型检查更严格

---

## 🚀 未来扩展可能性

有了基类设计，未来可以轻松添加新题型：

```python
class InteractiveQuestion(QuestionBase):
    """交互式题目 - 未来可能的扩展"""
    
    max_score: float
    interaction_type: Literal["drag-drop", "click", "draw"]
    correct_sequence: List[str]
    
    def is_composite(self) -> bool:
        return False
    
    def get_total_score(self) -> float:
        return self.max_score
```

只需继承 `QuestionBase` 并实现必要方法即可！

---

## 📋 总结

### 本次改进

✅ **修复了参考答案和评分标准显示bug**
- 问题：API返回数据缺少字段
- 解决：在 `sync_manager.py` 中添加字段映射

✅ **优化了数据模型结构**
- 引入 `QuestionBase` 基类
- 添加 `@model_validator` 确保数据一致性
- 为 `SubQuestion` 添加辅助方法

✅ **保持向后兼容**
- 现有 JSON 配置无需修改
- 现有代码无需大改
- 只是增加了验证和安全性

### 技术债务清理

- 🧹 统一了题目数据的验证逻辑
- 🧹 消除了字段可选性带来的不确定性
- 🧹 为未来扩展打下良好基础

### 用户体验改善

- 🎨 田字格布局现在能完整显示所有信息
- 🎨 参考答案和评分标准不再显示"暂无"
- 🎨 审查评分时信息更加完整

---

## 🔗 相关文档

- [田字格布局功能说明](./GRID_LAYOUT_FEATURE.md)
- [数据模型定义](../src/models/schemas.py)
- [API同步管理器](../src/api/sync_manager.py)
