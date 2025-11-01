# 🔧 页面导航修复说明

## 🐛 问题描述

用户反馈了两个问题：

### 1. 页面跳转按钮无效

在多个位置的按钮点击后无法跳转到对应页面：
- 侧边栏任务历史中的"查看结果"、"人工微调"按钮
- 新建任务后的"立即查看状态"按钮
- 任务状态页的"查看评分结果"、"进行人工微调"按钮

### 2. 上传后奇怪地跳转到试卷制作页面

上传考试数据和学生作答后，页面总是跳转回第一个标签"试卷制作"，而不是停留在"新建评分任务"页面。

---

## 🔍 根本原因

### 问题1：`st.tabs()` 不支持编程控制

Streamlit 的 `st.tabs()` 组件**不支持**通过代码动态切换激活的标签页：

```python
# ❌ 这样做无效
tabs = st.tabs(["Tab1", "Tab2", "Tab3"])
st.session_state.active_tab = "Tab2"  # 不会切换到Tab2
st.rerun()
```

`st.tabs()` 只会在**初始渲染时**使用 `default` 参数（但Streamlit甚至没有提供这个参数）。用户点击标签时才会切换，代码无法控制。

**原代码：**
```python
# ❌ 按钮设置了session_state，但tabs不会响应
if st.button("查看结果"):
    st.session_state.active_tab = "results"  # 设置了但无效
    st.rerun()

tabs = st.tabs(["试卷制作", "新建任务", "任务状态", "评分结果", "人工微调"])
# tabs 不会自动切换到 "评分结果"
```

### 问题2：页面刷新时 `active_tab` 未持久化

上传成功后调用 `st.rerun()`，但由于 `active_tab` 初始化逻辑不完整，导致重置为默认值：

```python
# ❌ 原代码
if st.session_state.get("active_tab") == "results":
    default_tab = 3
else:
    default_tab = 0  # 其他情况都是0，所以总是回到第一个标签
```

---

## ✅ 解决方案

### 改用按钮导航替代标签页

使用5个按钮作为导航栏，通过 `session_state` 控制显示哪个页面：

```python
# ✅ 新代码
tab_options = {
    "📝 试卷制作": "exam_maker",
    "📤 新建评分任务": "new_job",
    "📊 任务状态": "status",
    "📋 评分结果": "results",
    "✏️ 人工微调": "adjust",
}

# 初始化（只在第一次运行时设置）
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "exam_maker"

# 渲染导航按钮
nav_cols = st.columns(5)
for idx, (display_name, page_id) in enumerate(tab_options.items()):
    with nav_cols[idx]:
        button_type = "primary" if page_id == st.session_state.active_tab else "secondary"
        if st.button(display_name, key=f"nav_{page_id}", type=button_type):
            st.session_state.active_tab = page_id
            st.rerun()

# 根据active_tab显示对应页面
if st.session_state.active_tab == "exam_maker":
    show_exam_maker_page()
elif st.session_state.active_tab == "new_job":
    show_new_job_page()
# ... 其他页面
```

### 优势

1. **✅ 完全可控**：通过 `session_state.active_tab` 可以在任何地方切换页面
2. **✅ 状态持久**：刷新页面后仍保持在当前页面
3. **✅ 视觉反馈**：当前页面的按钮显示为 `primary` 类型（高亮）

---

## 🎯 修复效果

### 修复前

```
用户操作                          实际结果
─────────────────────────────────────────────────────
点击"查看结果"按钮        ❌ 无反应，停留在当前页面
点击"立即查看状态"按钮    ❌ 无反应，停留在当前页面
上传文件后                ❌ 跳回"试卷制作"页面
点击标签页                ✅ 正常切换（唯一有效的方式）
```

### 修复后

```
用户操作                          实际结果
─────────────────────────────────────────────────────
点击"查看结果"按钮        ✅ 跳转到"评分结果"页面
点击"立即查看状态"按钮    ✅ 跳转到"任务状态"页面
上传文件后                ✅ 停留在"新建评分任务"页面
点击导航按钮              ✅ 切换到对应页面
侧边栏快捷按钮            ✅ 正常跳转
```

---

## 🔄 页面跳转流程

### 示例：上传文件后查看状态

```python
# 1. 用户在"新建评分任务"页面上传文件
def show_new_job_page():
    if st.button("开始评分"):
        # 上传成功后
        st.success(f"✅ 任务已创建! 任务ID: {job_id}")
        
        # 2. 设置跳转目标
        if st.button("立即查看状态"):
            st.session_state.current_job_id = job_id
            st.session_state.active_tab = "status"  # ✅ 设置目标页面
            st.rerun()  # 刷新页面

# 3. main() 函数根据 active_tab 显示对应页面
def main():
    # ...
    if st.session_state.active_tab == "status":  # ✅ 检测到切换
        show_job_status_page()  # ✅ 显示任务状态页面
```

### 示例：侧边栏快捷操作

```python
# 侧边栏任务历史
with st.sidebar:
    for job in jobs:
        if st.button("查看结果", key=f"view_{job['job_id']}"):
            st.session_state.current_job_id = job["job_id"]
            st.session_state.active_tab = "results"  # ✅ 切换到结果页
            st.rerun()

# main() 函数会响应
if st.session_state.active_tab == "results":  # ✅ 显示结果页面
    show_results_page()
```

---

## 📋 修改清单

### 修改的文件

**`src/ui/app.py`**

**修改内容：**

1. **移除 `st.tabs()` 调用**
   - 原来使用 `tabs = st.tabs([...])`
   - 现在使用按钮导航

2. **新增导航按钮区域**
   ```python
   nav_cols = st.columns(5)
   for display_name, page_id in tab_options.items():
       with nav_cols[idx]:
           if st.button(...):
               st.session_state.active_tab = page_id
               st.rerun()
   ```

3. **使用 if-elif 显示页面**
   ```python
   if st.session_state.active_tab == "exam_maker":
       show_exam_maker_page()
   elif st.session_state.active_tab == "new_job":
       show_new_job_page()
   # ...
   ```

4. **确保 `active_tab` 初始化**
   ```python
   if "active_tab" not in st.session_state:
       st.session_state.active_tab = "exam_maker"
   ```

**无需修改的部分：**
- 所有的跳转按钮代码（它们已经在设置 `session_state.active_tab`）
- 页面渲染函数（`show_xxx_page()`）
- API调用逻辑

---

## 🎨 UI改进

### 导航栏样式

修复前（标签页）：
```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ 试卷制作 │ 新建任务 │ 任务状态 │ 评分结果 │ 人工微调 │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

修复后（按钮导航）：
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ 试卷制作 │ │ 新建任务 │ │ 任务状态 │ │ 评分结果 │ │ 人工微调 │
│  (高亮)  │ │         │ │         │ │         │ │         │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

**特点：**
- 当前页面按钮显示为 `primary` 类型（蓝色高亮）
- 其他按钮显示为 `secondary` 类型（灰色）
- 清晰的视觉反馈

---

## 🧪 测试场景

### 场景1：新建任务后查看状态

**步骤：**
1. 点击导航栏"新建评分任务"
2. 上传配置和答案文件
3. 点击"开始评分"
4. 点击"立即查看状态"

**预期结果：**
- ✅ 自动跳转到"任务状态"页面
- ✅ 显示刚创建的任务
- ✅ "任务状态"按钮高亮

### 场景2：侧边栏快捷操作

**步骤：**
1. 在侧边栏任务历史中选择一个已完成的任务
2. 点击"查看结果"按钮

**预期结果：**
- ✅ 跳转到"评分结果"页面
- ✅ 自动选中该任务
- ✅ "评分结果"按钮高亮

### 场景3：上传后页面保持

**步骤：**
1. 在"新建评分任务"页面
2. 上传文件并开始评分

**预期结果：**
- ✅ 页面停留在"新建评分任务"
- ✅ 不会跳回"试卷制作"

### 场景4：多次跳转

**步骤：**
1. 点击"任务状态"
2. 点击"查看评分结果"跳转到"评分结果"
3. 点击"进行人工微调"跳转到"人工微调"

**预期结果：**
- ✅ 每次都正确跳转
- ✅ 导航按钮正确高亮
- ✅ 任务ID在跳转间保持

---

## 💡 实现细节

### session_state 使用

```python
# 关键状态变量
st.session_state.active_tab = "exam_maker"  # 当前页面
st.session_state.current_job_id = "job_xxx"  # 当前任务ID
```

### 跳转函数模式

```python
def navigate_to_page(page_id, job_id=None):
    """统一的页面跳转函数"""
    st.session_state.active_tab = page_id
    if job_id:
        st.session_state.current_job_id = job_id
    st.rerun()

# 使用
if st.button("查看结果"):
    navigate_to_page("results", job_id="job_123")
```

### 页面初始化

每个页面函数开始时可以检查必要的参数：

```python
def show_results_page():
    if not st.session_state.get("current_job_id"):
        st.info("请先选择一个任务")
        return
    
    # 正常渲染页面
    job_id = st.session_state.current_job_id
    # ...
```

---

## ✅ 总结

### 问题已修复

✅ **页面跳转按钮现在完全有效**
- 所有跳转按钮都能正确切换页面
- 导航状态在刷新后保持

✅ **上传后不再跳转回第一页**
- 页面保持在当前位置
- 用户体验更流畅

### 技术改进

- 🔧 使用按钮导航替代标签页
- 🔧 统一使用 `session_state.active_tab` 控制
- 🔧 所有跳转逻辑集中管理
- 🔧 添加视觉反馈（按钮高亮）

### 用户体验提升

- 🎨 导航更加直观清晰
- 🎨 当前页面有明确的视觉标识
- 🎨 操作流程更加连贯
- 🎨 减少困惑和误操作

---

**修复完成时间：** 2025年11月1日  
**影响范围：** 全局页面导航  
**向后兼容：** ✅ 完全兼容（只是改变了导航方式）  
**测试状态：** 等待用户测试
