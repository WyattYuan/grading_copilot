"""
UI 配置功能演示和测试

运行此脚本前请确保：
1. API 服务已启动 (python run_api.py)
2. UI 服务已启动 (python run_ui.py)
"""

import requests
import time


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_api_health():
    """测试 API 健康状态"""
    print_section("1. 测试 API 服务健康状态")

    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API 服务运行正常")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ API 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 API 服务: {str(e)}")
        print("   请确保已运行: python run_api.py")
        return False


def test_config_update():
    """测试配置更新功能"""
    print_section("2. 测试配置更新功能")

    test_configs = [
        {
            "name": "完整配置",
            "data": {
                "api_key": "sk-test-demo-key-12345678901234567890",
                "model_name": "qwen-plus",
            },
        },
        {"name": "仅更新模型", "data": {"model_name": "gpt-4o"}},
        {
            "name": "仅更新 API Key",
            "data": {"api_key": "sk-test-another-key-09876543210987654321"},
        },
    ]

    for test in test_configs:
        print(f"\n测试场景: {test['name']}")
        print(f"发送数据: {test['data']}")

        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/config/update",
                json=test["data"],
                timeout=5,
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 更新成功")
                print(f"   状态: {result['status']}")
                print(f"   更新字段: {result['updated_fields']}")
            else:
                print(f"❌ 更新失败: {response.status_code}")
                print(f"   错误: {response.text}")

        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")

        time.sleep(0.5)


def test_config_status():
    """测试配置状态查询"""
    print_section("3. 测试配置状态查询")

    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/config/status", timeout=5)

        if response.status_code == 200:
            status = response.json()
            print("✅ 配置状态查询成功")
            print(f"\n当前配置:")
            print(f"   API Key 配置: {'是' if status['api_key_configured'] else '否'}")
            print(f"   API Key 预览: {status['api_key_preview']}")
            print(f"   模型名称: {status['model_name']}")
        else:
            print(f"❌ 查询失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")


def test_ui_config_workflow():
    """模拟 UI 配置工作流"""
    print_section("4. 模拟 UI 配置工作流")

    # 步骤 1: 用户输入配置
    print("\n步骤 1: 用户在 UI 输入配置")
    user_config = {
        "api_key": "sk-user-input-key-abcdefghijklmnopqrstuvwx",
        "model_name": "qwen-plus",
    }
    print(f"   API Key: {user_config['api_key'][:15]}...")
    print(f"   模型: {user_config['model_name']}")

    # 步骤 2: 保存到本地 session_state (模拟)
    print("\n步骤 2: 保存到本地 session_state")
    print("   ✅ session_state.api_key = ...")
    print("   ✅ session_state.model_name = ...")

    # 步骤 3: 同步到 API 服务
    print("\n步骤 3: 同步到 API 服务")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/config/update", json=user_config, timeout=5
        )

        if response.status_code == 200:
            print("   ✅ 配置已同步到 API")
        else:
            print(f"   ⚠️  同步失败: {response.status_code}")

    except Exception as e:
        print(f"   ⚠️  无法连接到 API: {str(e)}")

    # 步骤 4: 验证配置生效
    print("\n步骤 4: 验证配置生效")
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/config/status", timeout=5)

        if response.status_code == 200:
            status = response.json()
            if status["model_name"] == user_config["model_name"]:
                print("   ✅ 配置验证成功")
                print(f"   当前模型: {status['model_name']}")
            else:
                print("   ❌ 配置不一致")
        else:
            print(f"   ❌ 验证失败: {response.status_code}")

    except Exception as e:
        print(f"   ❌ 请求失败: {str(e)}")


def test_model_presets():
    """测试预设模型配置"""
    print_section("5. 测试预设模型列表")

    presets = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "qwen-plus",
        "qwen-turbo",
        "qwen-max",
    ]

    print("\n可用的预设模型:")
    for i, model in enumerate(presets, 1):
        print(f"   {i}. {model}")

    print("\n测试切换模型...")
    for model in presets[:3]:  # 测试前3个
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/config/update",
                json={"model_name": model},
                timeout=5,
            )

            if response.status_code == 200:
                print(f"   ✅ {model}")
            else:
                print(f"   ❌ {model}")

        except Exception as e:
            print(f"   ❌ {model}: {str(e)}")

        time.sleep(0.3)


def print_ui_access_info():
    """打印 UI 访问信息"""
    print_section("UI 访问信息")

    print("\n📱 请在浏览器中打开:")
    print("   http://localhost:8501")

    print("\n🔧 配置步骤:")
    print("   1. 在左侧边栏找到 '🔧 API 配置' 部分")
    print("   2. 输入 API Key (密码格式)")
    print("   3. 从下拉菜单选择模型或自定义")
    print("   4. 点击 '💾 保存配置' 按钮")
    print("   5. 查看底部的配置状态确认")

    print("\n📚 更多信息:")
    print("   查看: docs/UI_CONFIG.md")


def main():
    """主测试函数"""
    print("=" * 60)
    print("  AI 智能评分系统 - UI 配置功能测试")
    print("=" * 60)

    # 测试 1: API 健康检查
    if not test_api_health():
        print("\n⚠️  API 服务未启动，某些测试将失败")
        print("   请先运行: python run_api.py")

    time.sleep(1)

    # 测试 2: 配置更新
    test_config_update()
    time.sleep(1)

    # 测试 3: 配置状态
    test_config_status()
    time.sleep(1)

    # 测试 4: UI 工作流
    test_ui_config_workflow()
    time.sleep(1)

    # 测试 5: 预设模型
    test_model_presets()
    time.sleep(1)

    # 显示 UI 访问信息
    print_ui_access_info()

    # 总结
    print_section("测试完成")
    print("\n✅ 所有 API 测试已完成")
    print("💡 现在可以在 UI 界面进行手动测试")
    print("\n下一步:")
    print("   1. 访问 http://localhost:8501")
    print("   2. 在侧边栏配置 API Key 和模型")
    print("   3. 开始使用评分功能")


if __name__ == "__main__":
    main()
