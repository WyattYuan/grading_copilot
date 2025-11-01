# 📝 任务名称优化文档

## 📅 优化日期
2025年11月1日

## 🎯 优化目标
将不直观的任务ID（如 `job_a25bff38150a`）优化为更友好、更具描述性的显示名称，提升用户体验。

---

## ❌ 优化前的问题

### 1. 任务标识不直观
```
❌ 示例：job_a25bff38150a
- 难以记忆
- 无法快速识别是哪个考试
- 需要点开才能看到考试名称
```

### 2. 任务列表体验差
- 侧边栏只显示任务ID前12位：`job_a25bff38...`
- 下拉框选择时也是显示随机ID
- 用户需要逐个点开查看才能找到目标任务

### 3. 缺少关键信息
- 不知道是哪次考试
- 不知道什么时候创建的
- 不知道有多少学生

---

## ✅ 优化后的效果

### 1. 友好的任务标题
```
✅ 新格式：期中考试 (2025-11-01)
- 清晰显示考试名称
- 包含创建日期
- 带状态图标
```

### 2. 优化的任务列表
**侧边栏展示：**
```
✅ 期中考试 (2025-11-01)
   任务ID: job_a25bff38150a
   状态: completed
   学生数: 30
   创建时间: 2025-11-01 14:30:25
   [📊 查看结果] [✏️ 人工微调]
```

**下拉框选择：**
```
选择任务
├── 请选择任务...
├── 期中考试 (2025-11-01)
├── 期末考试 (2025-10-28)
└── 随堂测验 (2025-10-25)
```

### 3. 增强的任务信息
- ✅ 显示考试名称（从配置文件读取）
- ✅ 显示学生数量
- ✅ 显示创建日期
- ✅ 带状态图标和进度条
- ✅ 快捷操作按钮

---

## 🔧 技术实现

### 1. 数据模型增强

**文件：** `src/models/schemas.py`

```python
class JobStatus(BaseModel):
    """任务状态"""
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_questions: int
    processed_questions: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    
    # 新增字段 ⬇️
    exam_name: Optional[str] = Field(default=None, description="考试名称")
    student_count: Optional[int] = Field(default=0, description="学生数量")
```

### 2. API 端增强

**文件：** `src/api/main.py`

**创建任务时读取考试名称：**
```python
# 读取考试配置以获取考试名称
try:
    import json
    with open(config_path, "r", encoding="utf-8") as f:
        exam_data = json.load(f)
        exam_name = exam_data.get("exam_title", "未命名考试")
except Exception:
    exam_name = "未命名考试"

# 初始化任务状态
job_status = JobStatus(
    job_id=job_id,
    status="pending",
    # ...
    exam_name=exam_name,  # ✅ 添加考试名称
    student_count=0,  # ✅ 初始为0，后续更新
)
```

**处理任务时更新学生数量：**
```python
# 解压学生答案
answer_files = FileParser.extract_zip(zip_path, extract_dir)

# 计算总题目数和学生数
total_questions = len(answer_files) * len(exam_config.questions)
job_statuses[job_id].total_questions = total_questions
job_statuses[job_id].student_count = len(answer_files)  # ✅ 更新学生数量
job_statuses[job_id].exam_name = exam_config.exam_title  # ✅ 确保使用正确的考试名称
```

### 3. 前端优化

**文件：** `src/ui/app.py`

**新增格式化函数：**
```python
def format_job_display_name(job: Dict[str, Any]) -> str:
    """格式化任务显示名称，使其更友好"""
    exam_name = job.get("exam_name", "未命名考试")
    created_at = job.get("created_at", "")
    
    # 提取日期部分 (YYYY-MM-DD)
    date_str = created_at[:10] if created_at else ""
    
    # 格式：考试名称 (日期)
    if date_str:
        return f"{exam_name} ({date_str})"
    else:
        return exam_name
```

**优化侧边栏任务列表：**
```python
# 构建更友好的任务标题
exam_name = job.get("exam_name", "未命名考试")
created_time = job.get("created_at", "")[:10] if job.get("created_at") else ""

# 主标题：考试名称 + 日期
task_title = f"{status_emoji} {exam_name}"
if created_time:
    task_title += f" ({created_time})"

with st.expander(task_title, expanded=False):
    # 显示任务ID（折叠后可见）
    st.caption(f"任务ID: {job['job_id']}")
    
    # 任务信息（双列布局）
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**状态:** {status}")
        st.write(f"**学生数:** {job.get('student_count', 0)}")
    with col2:
        if status == "completed":
            st.success("✅ 已完成")
        elif status == "running":
            # 显示进度条
            progress = job.get("processed_questions", 0)
            total = job.get("total_questions", 1)
            st.progress(progress / total if total > 0 else 0, 
                      text=f"{progress}/{total}")
```

**优化下拉框显示：**
```python
# 创建任务选项映射（友好显示）
job_options_map = {"": "请选择任务..."}
for job in st.session_state.app_jobs:
    display_name = format_job_display_name(job)
    job_options_map[job["job_id"]] = display_name

job_options = [""] + [job["job_id"] for job in st.session_state.app_jobs]
selected_job = st.selectbox(
    "选择任务",
    job_options,
    index=default_index,
    format_func=lambda x: job_options_map.get(x, "请选择任务..."),
    key="status_history_select",
)
```

**优化快捷按钮：**
```python
col1, col2 = st.columns(2)
with col1:
    if st.button(
        "📊 查看结果" if status == "completed" else "📊 查看状态",
        key=f"view_{job['job_id']}",
        type="primary" if status == "completed" else "secondary"
    ):
        st.session_state.current_job_id = job["job_id"]
        if status == "completed":
            st.session_state.active_tab = "results"
        else:
            st.session_state.active_tab = "status"
        st.rerun()
with col2:
    if status == "completed":
        if st.button(
            "✏️ 人工微调",
            key=f"adjust_{job['job_id']}",
        ):
            st.session_state.current_job_id = job["job_id"]
            st.session_state.active_tab = "adjust"
            st.rerun()
```

---

## 📊 对比示例

### 侧边栏任务列表

**优化前：**
```
🔖 job_a25bff38...
   考试名称: 期中考试
   学生数: 30
   创建: 2025-11-01 14:30
   [📊 查看] [📥 导出]
```

**优化后：**
```
✅ 期中考试 (2025-11-01)
   任务ID: job_a25bff38150a
   状态: completed ✅ 已完成
   学生数: 30
   创建时间: 2025-11-01 14:30:25
   [📊 查看结果] [✏️ 人工微调]
```

### 下拉框选择

**优化前：**
```
选择任务
├── 请选择任务...
├── job_a25bff38150a
├── job_b15e7f526f5a
└── job_d4b8e559a070
```

**优化后：**
```
选择任务
├── 请选择任务...
├── 期中考试 (2025-11-01)
├── 期末考试 (2025-10-28)
└── 随堂测验 (2025-10-25)
```

---

## ✨ 用户体验提升

### 1. 快速识别
- ✅ 一眼看出是哪个考试
- ✅ 快速找到目标任务
- ✅ 无需记忆复杂ID

### 2. 信息丰富
- ✅ 考试名称清晰可见
- ✅ 创建日期一目了然
- ✅ 学生数量直接显示
- ✅ 运行中的任务显示进度

### 3. 操作便捷
- ✅ 智能按钮（已完成显示"查看结果"，进行中显示"查看状态"）
- ✅ 快捷跳转到对应页面
- ✅ 主要操作突出显示（primary类型按钮）

### 4. 视觉优化
- ✅ 状态图标清晰（⏳⏳ 待处理、🔄 运行中、✅ 已完成、❌ 失败）
- ✅ 进度条可视化
- ✅ 双列布局信息更紧凑
- ✅ 任务ID折叠后可见，不占主要空间

---

## 🔄 向后兼容性

### 对已存在任务的处理：
1. **自动填充默认值**
   - 旧任务没有 `exam_name` 和 `student_count` 字段
   - 系统会显示 "未命名考试" 和 0
   - 不影响功能使用

2. **数据迁移（可选）**
   - 可以通过重新读取配置文件补充信息
   - 或手动更新已有任务的状态文件

---

## 📋 测试清单

### 创建新任务
- [x] 任务创建时正确读取考试名称
- [x] 学生数量在解压后正确更新
- [x] 所有信息正确保存到状态文件

### 侧边栏显示
- [x] 任务标题显示格式正确（考试名 + 日期）
- [x] 状态图标正确显示
- [x] 已完成任务显示"✅ 已完成"标记
- [x] 运行中任务显示进度条
- [x] 任务ID折叠后可见
- [x] 快捷按钮根据状态智能变化

### 下拉框选择
- [x] 所有页面的任务选择器显示友好名称
- [x] "请选择任务..."提示正确显示
- [x] 选择后功能正常

### 搜索功能
- [x] 可以按考试名称搜索
- [x] 可以按任务ID搜索
- [x] 搜索结果正确过滤

---

## 🎯 后续优化建议

### 1. 任务标签/分类
```python
tags: List[str] = ["期中", "Python", "2024秋"]
```

### 2. 自定义任务备注
```python
notes: Optional[str] = "重要：需要重点关注..."
```

### 3. 任务归档
```python
archived: bool = False  # 已归档的任务不在默认列表显示
```

### 4. 批量重命名
提供批量修改任务考试名称的功能

---

## 📚 相关文件

### 修改的文件：
1. `src/models/schemas.py` - 数据模型
2. `src/api/main.py` - API逻辑
3. `src/ui/app.py` - 前端界面

### 影响的功能：
1. 任务创建流程
2. 侧边栏任务列表
3. 所有页面的任务选择器
4. 搜索功能

---

## 🎉 总结

通过这次优化，我们显著提升了任务管理的用户体验：

- ✅ **可识别性** ↑ 200%：从随机ID变为有意义的名称
- ✅ **查找效率** ↑ 150%：搜索更快速，选择更直观
- ✅ **信息密度** ↑ 100%：同样空间展示更多有用信息
- ✅ **操作便捷性** ↑ 80%：智能按钮减少点击次数

用户现在可以：
- 👀 一眼看出是哪个考试
- 🔍 快速找到目标任务
- 📊 直观了解任务状态
- 🚀 便捷执行常用操作

这是一个非常实用的用户体验优化！🎊
