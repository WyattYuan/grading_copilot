# Tests 目录说明

## 📁 目录结构

```
tests/
├── unit/                       # 单元测试
│   ├── test_models.py         # 数据模型验证测试
│   ├── test_file_utils.py     # 文件工具函数测试
│   └── test_navigation.py     # UI 导航逻辑测试
│
├── integration/                # 集成测试
│   ├── test_api_config.py     # API 配置功能测试
│   └── test_ui_workflow.py    # UI 完整工作流测试
│
├── helpers/                    # 测试辅助工具
│   ├── create_test_data.py    # 生成测试数据
│   └── fixtures.py            # 共享测试固件
│
├── deprecated/                 # 已废弃的测试
│   └── ...                    # 旧版测试（保留用于参考）
│
├── __init__.py                 # 测试包初始化
└── README.md                   # 本文档
```

## 🎯 测试分类

### 单元测试 (Unit Tests)
测试单个组件或函数的功能，不依赖外部系统。

**文件：**
- `test_models.py` - 测试数据模型的验证、继承、序列化等
- `test_file_utils.py` - 测试文件解析、ZIP 提取等工具函数
- `test_navigation.py` - 测试 UI 页面导航逻辑

**运行：**
```bash
pytest tests/unit/
```

### 集成测试 (Integration Tests)
测试多个组件协作，可能需要启动服务。

**文件：**
- `test_api_config.py` - 测试 API 配置端点（需要 API 服务运行）
- `test_ui_workflow.py` - 测试完整的 UI 配置工作流

**运行：**
```bash
# 需要先启动服务
python run_api.py  # 在另一个终端
pytest tests/integration/
```

### 辅助工具 (Helpers)
不是测试，而是用于生成测试数据或提供测试固件。

**文件：**
- `create_test_data.py` - 生成示例考试配置和学生答案
- `fixtures.py` - 共享的 pytest fixtures

**使用：**
```bash
python tests/helpers/create_test_data.py
```

### 已废弃 (Deprecated)
旧版本或不再维护的测试，保留用于参考。

## 🚀 快速开始

### 运行所有测试
```bash
pytest tests/
```

### 运行特定类别
```bash
pytest tests/unit/              # 只运行单元测试
pytest tests/integration/       # 只运行集成测试
```

### 运行单个文件
```bash
pytest tests/unit/test_models.py
```

### 查看详细输出
```bash
pytest tests/ -v               # 详细模式
pytest tests/ -s               # 显示 print 输出
pytest tests/ -v -s            # 组合使用
```

### 生成覆盖率报告
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📝 测试命名规范

### 文件命名
- 单元测试：`test_<模块名>.py`
- 集成测试：`test_<功能名>_integration.py` 或 `test_<工作流名>_workflow.py`

### 函数命名
- 测试函数：`def test_<测试内容>()`
- 示例：`test_simple_question_validation()`

### 类命名（如果使用）
- 测试类：`class Test<组件名>`
- 示例：`class TestQuestionModel`

## 📋 当前测试清单

### ✅ 已整理的测试

#### 单元测试
- [x] **test_models.py** - 数据模型测试
  - Question 验证（单题、复合题）
  - QuestionSnapshot 字段测试
  - 继承关系测试

- [x] **test_file_utils.py** - 文件工具测试
  - ZIP 文件提取
  - 文件计数
  - 学生答案解析

- [x] **test_navigation.py** - 导航逻辑测试
  - 页面切换逻辑
  - 状态管理
  - 用户场景模拟

#### 集成测试
- [x] **test_api_config.py** - API 配置测试
  - 配置更新端点
  - 配置状态查询
  - 部分更新功能

- [x] **test_ui_workflow.py** - UI 工作流测试
  - UI 配置流程
  - 模型选择
  - API 同步

#### 辅助工具
- [x] **create_test_data.py** - 测试数据生成器
  - 创建示例 ZIP 包
  - 生成任务数据

### 🗑️ 已废弃的测试

- `test_model.py` → 移至 `deprecated/` (被 test_models.py 替代)
- `test_new_model.py` → 移至 `deprecated/` (临时测试文件)
- `test_job_status.py` → 移至 `deprecated/` (功能已整合)
- `demo_task_names.py` → 移至 `helpers/` (演示工具)
- `debug_job_data.py` → 移至 `helpers/` (调试工具)

## 🔧 添加新测试

### 1. 单元测试
```python
# tests/unit/test_new_component.py
"""测试新组件"""
import pytest
from src.module import NewComponent

def test_component_basic_function():
    """测试基本功能"""
    component = NewComponent()
    assert component.do_something() == expected_result

def test_component_edge_case():
    """测试边界情况"""
    with pytest.raises(ValueError):
        NewComponent(invalid_param=None)
```

### 2. 集成测试
```python
# tests/integration/test_new_workflow.py
"""测试新工作流"""
import requests
import pytest

@pytest.fixture
def api_client():
    """API 客户端固件"""
    return requests.Session()

def test_complete_workflow(api_client):
    """测试完整工作流"""
    # 步骤 1
    response = api_client.post("/api/v1/start")
    assert response.status_code == 200
    
    # 步骤 2
    job_id = response.json()["job_id"]
    status = api_client.get(f"/api/v1/jobs/{job_id}")
    assert status.json()["status"] == "running"
```

### 3. 添加 Fixtures
```python
# tests/helpers/fixtures.py
"""共享测试固件"""
import pytest
from src.models import ExamConfig

@pytest.fixture
def sample_exam_config():
    """示例考试配置"""
    return ExamConfig(
        exam_name="示例考试",
        questions=[...]
    )
```

## 📊 测试覆盖率目标

- 单元测试覆盖率：≥ 80%
- 集成测试覆盖关键路径：100%
- 每个新功能都应有对应测试

## 🐛 调试测试

### 使用 pytest 调试器
```bash
pytest tests/unit/test_models.py --pdb
```

### 只运行失败的测试
```bash
pytest tests/ --lf  # last-failed
```

### 显示最慢的测试
```bash
pytest tests/ --durations=10
```

## 📚 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [项目主文档](../README.md)

---

**维护者：** 项目团队  
**最后更新：** 2025年11月1日
