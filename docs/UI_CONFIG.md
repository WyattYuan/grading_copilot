# UI 配置指南

## 概述

从本版本开始，您可以通过 Web 界面直接配置 API Key 和模型名称，无需编辑 `.env` 文件。

## 配置步骤

### 1. 启动应用

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### 2. 打开配置界面

1. 访问 `http://localhost:8501`
2. 在左侧边栏找到 **"🔧 API 配置"** 部分

### 3. 输入配置

#### API Key
- 在 **"API Key"** 输入框中输入您的 OpenAI API Key
- 密码格式输入，输入内容不会显示
- 格式通常为: `sk-...`

#### 模型选择
有两种方式选择模型：

**方式 1: 从预设列表选择（推荐）**
- 从下拉菜单选择常用模型：
  - `gpt-4o` (GPT-4 Omni - 最新最强)
  - `gpt-4o-mini` (GPT-4 Omni Mini - 性价比高)
  - `gpt-4-turbo` (GPT-4 Turbo)
  - `gpt-3.5-turbo` (GPT-3.5 - 最便宜)
  - `qwen-plus` (通义千问 Plus - 推荐)
  - `qwen-turbo` (通义千问 Turbo)
  - `qwen-max` (通义千问 Max)

**方式 2: 自定义模型名称**
- 勾选 **"使用自定义模型名称"**
- 在文本框中输入任意模型名称
- 例如: `gpt-4-1106-preview`, `claude-3-opus` 等

### 4. 保存配置

点击 **"💾 保存配置"** 按钮：
- 配置会同时保存到 UI 和 API 服务
- 显示 "✅ 配置已保存并同步到 API！"
- 页面会自动刷新

### 5. 验证配置

在侧边栏底部查看 **"📊 当前配置"**：
- **API Key:** ✅ 已配置 / ❌ 未配置
- **模型:** 显示当前选择的模型名称

## 重置配置

如需恢复默认配置：
1. 点击 **"🔄 重置"** 按钮
2. 配置将恢复为 `.env` 文件中的值（如果存在）

## 配置持久化

### 当前会话
- 配置在当前浏览器会话中有效
- 关闭浏览器后需要重新配置

### 永久保存（可选）
如果希望配置永久生效，可以编辑 `.env` 文件：

```bash
OPENAI_API_KEY=你的API密钥
OPENAI_MODEL=qwen-plus
```

## 安全提示

⚠️ **重要安全建议：**

1. **不要分享 API Key**
   - API Key 是敏感信息，请勿分享给他人
   - 不要在截图或录屏中暴露 API Key

2. **定期更换密钥**
   - 建议定期更换 API Key
   - 如发现泄露，立即在服务提供商处吊销

3. **使用环境变量（生产环境）**
   - 生产部署时使用环境变量或密钥管理服务
   - 不要将 `.env` 文件提交到版本控制系统

## 故障排除

### 问题 1: 保存后显示 "无法连接到 API"

**原因：** API 服务未启动

**解决方案：**
```bash
# 检查 API 服务状态
curl http://localhost:8000/

# 如果失败，重启服务
start.bat  # Windows
./start.sh # Linux/Mac
```

### 问题 2: 配置保存失败

**可能原因：**
1. API Key 为空
2. 网络连接问题
3. API 服务异常

**解决方案：**
1. 确保 API Key 已填写
2. 检查网络连接
3. 查看 API 日志: `docker logs grading_api`

### 问题 3: 评分时提示 API Key 错误

**原因：** API Key 无效或已过期

**解决方案：**
1. 验证 API Key 是否正确
2. 检查 API Key 是否在服务提供商处有效
3. 尝试重新生成 API Key

## API 端点说明

如果需要通过 API 直接管理配置：

### 更新配置
```bash
curl -X POST http://localhost:8000/api/v1/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk-...",
    "model_name": "qwen-plus"
  }'
```

### 查询配置状态
```bash
curl http://localhost:8000/api/v1/config/status
```

响应示例：
```json
{
  "api_key_configured": true,
  "model_name": "qwen-plus",
  "api_key_preview": "sk-test-..."
}
```

## 最佳实践

1. **首次使用前配置**
   - 启动应用后首先配置 API Key
   - 选择合适的模型（推荐 `qwen-plus`）

2. **测试配置**
   - 配置后先用示例数据测试
   - 确认评分功能正常工作

3. **性能优化**
   - 小批量任务使用 `gpt-4o` 获得最佳质量
   - 大批量任务使用 `qwen-plus` 或 `gpt-3.5-turbo` 平衡成本

4. **成本控制**
   - 关注 API 调用次数和成本
   - 在服务提供商处设置消费限额

## 更多帮助

- 查看 [快速开始指南](QUICKSTART.md)
- 查看 [使用文档](USAGE.md)
- 查看 [部署指南](DEPLOYMENT.md)
