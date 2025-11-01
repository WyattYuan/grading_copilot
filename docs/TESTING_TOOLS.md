# 测试配置文件说明

## 📋 文件概览

这三个文件构成了项目的测试基础设施，让测试更加标准化和便捷。

---

## 1️⃣ `pytest.ini` - pytest 配置文件

### 🎯 主要作用
这是 pytest 测试框架的**配置文件**，定义了测试运行的各种规则和行为。

### 📝 具体功能

#### A. 测试发现规则
```ini
testpaths = tests              # 在 tests/ 目录下查找测试
python_files = test_*.py       # 测试文件必须以 test_ 开头
python_classes = Test*         # 测试类必须以 Test 开头
python_functions = test_*      # 测试函数必须以 test_ 开头
```

**效果：** 当你运行 `pytest` 时，它会自动找到所有符合规范的测试文件。

#### B. 默认命令行选项
```ini
addopts = 
    -v                    # 详细输出模式（显示每个测试的名称）
    --strict-markers      # 严格检查标记（防止拼写错误）
    --tb=short           # 简短的错误追踪信息
    --disable-warnings   # 隐藏警告信息
```

**效果：** 每次运行 `pytest` 都会自动应用这些选项，不用手动输入。

#### C. 测试标记定义
```ini
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
    deprecated: 已废弃的测试
```

**使用示例：**
```python
import pytest

@pytest.mark.unit
def test_something():
    assert True

@pytest.mark.slow
def test_slow_operation():
    # 耗时操作
    pass
```

**运行特定标记的测试：**
```bash
pytest -m unit          # 只运行单元测试
pytest -m "not slow"    # 跳过慢速测试
```

#### D. 覆盖率配置
```ini
[coverage:run]
source = src           # 只统计 src/ 目录的覆盖率
omit = */tests/*       # 排除测试文件本身

[coverage:report]
precision = 2          # 显示小数点后2位
show_missing = True    # 显示未覆盖的代码行
```

**效果：** 运行 `pytest --cov` 时会应用这些配置。

### 💡 实际效果对比

**没有 pytest.ini：**
```bash
# 需要手动指定所有参数
pytest tests/ -v --tb=short --cov=src --cov-report=html
```

**有 pytest.ini：**
```bash
# 简单命令即可
pytest                  # 自动应用所有配置
pytest --cov           # 自动配置覆盖率
```

---

## 2️⃣ `run_tests.bat` - Windows 测试运行器

### 🎯 主要作用
为 Windows 用户提供**友好的交互式菜单**来运行不同类型的测试。

### 📝 具体功能

#### A. 交互式菜单
运行后显示：
```
═══════════════════════════════════════════════════════════
          AI智能评分系统 - 测试运行器
═══════════════════════════════════════════════════════════

请选择测试类型:

  1. 运行所有测试
  2. 只运行单元测试
  3. 只运行集成测试
  4. 运行并生成覆盖率报告
  5. 运行特定测试文件
  6. 退出

请输入选项 (1-6):
```

#### B. 一键运行测试
- **选项 1（所有测试）**：执行 `uv run pytest tests/ -v`
- **选项 2（单元测试）**：执行 `uv run pytest tests/unit/ -v`
- **选项 3（集成测试）**：执行 `uv run pytest tests/integration/ -v`
- **选项 4（覆盖率）**：执行 `uv run pytest tests/ --cov=src --cov-report=html`

#### C. 自动打开覆盖率报告
当选择"生成覆盖率报告"时，会自动在浏览器中打开 `htmlcov/index.html`。

### 💡 使用场景

**适合：**
- 不熟悉命令行的开发者
- 快速运行测试，无需记住命令
- 团队中的非技术人员（测试人员、项目经理等）

**使用方法：**
```cmd
# Windows 双击运行，或在命令行中：
run_tests.bat
```

---

## 3️⃣ `run_tests.sh` - Linux/Mac 测试运行器

### 🎯 主要作用
与 `run_tests.bat` 功能相同，但适用于 **Linux 和 macOS** 系统。

### 📝 具体功能

完全相同的交互式菜单和功能，但使用 Bash 脚本语法编写。

### 💡 使用方法

```bash
# 1. 添加执行权限（首次使用）
chmod +x run_tests.sh

# 2. 运行
./run_tests.sh
```

---

## 🔄 三者的关系

```
┌─────────────────────────────────────────────────────────┐
│                    pytest.ini                            │
│  (定义测试运行的规则和配置)                              │
│                                                          │
│  • 测试文件命名规范                                      │
│  • 默认命令行选项                                        │
│  • 覆盖率配置                                            │
│  • 测试标记定义                                          │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ 被以下脚本使用
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼────────┐               ┌─────────▼──────────┐
│ run_tests.bat  │               │  run_tests.sh      │
│  (Windows)     │               │  (Linux/Mac)       │
│                │               │                    │
│ 提供友好的菜单 │               │ 提供友好的菜单     │
│ 执行 pytest    │               │ 执行 pytest        │
│ 自动应用配置   │               │ 自动应用配置       │
└────────────────┘               └────────────────────┘
```

---

## 📊 实际使用示例

### 场景 1: 日常开发测试

```bash
# 开发者修改代码后快速测试

# 方式 1: 使用脚本（推荐新手）
run_tests.bat          # Windows
./run_tests.sh         # Linux/Mac
# 选择 "2. 只运行单元测试"

# 方式 2: 直接命令（推荐熟悉命令行的开发者）
pytest tests/unit/     # pytest.ini 自动应用 -v 等配置
```

### 场景 2: 提交代码前完整测试

```bash
# 方式 1: 使用脚本
run_tests.bat          
# 选择 "1. 运行所有测试"

# 方式 2: 直接命令
pytest                 # 运行所有测试（pytest.ini 指定 tests/ 目录）
```

### 场景 3: 检查代码覆盖率

```bash
# 方式 1: 使用脚本（推荐）
run_tests.bat
# 选择 "4. 运行并生成覆盖率报告"
# 自动打开浏览器显示覆盖率报告

# 方式 2: 直接命令
pytest --cov           # pytest.ini 自动配置覆盖率
```

### 场景 4: 只测试某个功能

```bash
# 方式 1: 使用脚本
run_tests.bat
# 选择 "5. 运行特定测试文件"
# 输入: tests/unit/test_models.py

# 方式 2: 直接命令
pytest tests/unit/test_models.py
```

---

## ✨ 关键优势

### 有了这三个文件：

1. **标准化** ✅
   - 所有开发者使用相同的测试配置
   - 避免"在我机器上能运行"的问题

2. **简化操作** ✅
   - 新手不用记住复杂的命令
   - 点击脚本即可运行测试

3. **自动化** ✅
   - 覆盖率配置自动应用
   - 测试发现自动完成

4. **跨平台** ✅
   - Windows 用户用 `.bat`
   - Linux/Mac 用户用 `.sh`
   - 功能完全一致

---

## 🎓 给新手的建议

### 如果你是新手开发者：
1. **使用脚本运行测试**（`run_tests.bat` 或 `run_tests.sh`）
2. **不用关心 pytest.ini 的细节**，它会自动工作
3. **选择"单元测试"**开始，这些测试运行最快

### 如果你熟悉命令行：
1. **直接使用 pytest 命令**，享受 pytest.ini 带来的便利
2. **使用测试标记**：`pytest -m unit`
3. **需要时查看 pytest.ini**，了解默认配置

---

## 📚 快速参考

| 你想做什么           | Windows 命令         | Linux/Mac 命令       |
| -------------------- | -------------------- | -------------------- |
| 运行所有测试         | `run_tests.bat` 选1  | `./run_tests.sh` 选1 |
| 只运行单元测试       | `run_tests.bat` 选2  | `./run_tests.sh` 选2 |
| 生成覆盖率报告       | `run_tests.bat` 选4  | `./run_tests.sh` 选4 |
| 直接命令（所有测试） | `pytest`             | `pytest`             |
| 直接命令（单元测试） | `pytest tests/unit/` | `pytest tests/unit/` |
| 直接命令（覆盖率）   | `pytest --cov`       | `pytest --cov`       |

---

**总结：** 这三个文件让测试变得简单、标准、友好！✨
