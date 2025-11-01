# 侧边栏问题修复说明

## 问题描述
重构后，Streamlit 侧边栏出现了不需要的导航项（如 "app", "adjustment" 等）。

## 根本原因
Streamlit 有一个内置的多页面应用机制：
- 自动检测项目中名为 `pages/` 的文件夹
- 将该文件夹中的 `.py` 文件自动添加到侧边栏导航
- 这是 Streamlit 的默认行为，无法通过配置完全禁用

## 解决方案
将 `pages/` 文件夹重命名为 `views/`，避免触发 Streamlit 的自动页面检测。

### 修改内容
1. **文件夹重命名**
   ```
   src/ui/pages/  →  src/ui/views/
   ```

2. **更新导入路径**
   - `app.py`: `from src.ui.pages.xxx` → `from src.ui.views.xxx`
   - `tests/test_refactoring.py`: 同步更新

3. **文档更新**
   - `docs/UI_REFACTORING.md`: 更新目录结构说明

## 效果
✅ 侧边栏不再显示不需要的页面导航
✅ 保持自定义的侧边栏内容（AI配置、任务历史）
✅ 所有功能正常工作

## 最佳实践
在使用 Streamlit 时，避免使用以下保留文件夹名：
- `pages/` - 自动多页面应用
- `.streamlit/` - 配置文件夹

如果确实需要模块化组织代码，使用其他名称如：
- `views/` ✅
- `screens/` ✅
- `modules/` ✅
- `ui_components/` ✅
