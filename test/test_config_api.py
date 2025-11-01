"""
测试配置 API 功能
"""

import pytest
import requests
from src.config import config


def test_config_update_api():
    """测试配置更新 API"""
    # 准备测试数据
    test_api_key = "sk-test-12345678901234567890"
    test_model = "gpt-4o"

    # 发送配置更新请求
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/config/update",
        json={"api_key": test_api_key, "model_name": test_model},
        timeout=5,
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "api_key" in data["updated_fields"]
    assert "model_name" in data["updated_fields"]

    print("✅ 配置更新 API 测试通过")


def test_config_status_api():
    """测试配置状态 API"""
    # 先更新配置
    test_api_key = "sk-test-status-12345678901234567890"
    test_model = "qwen-plus"

    requests.post(
        "http://127.0.0.1:8000/api/v1/config/update",
        json={"api_key": test_api_key, "model_name": test_model},
        timeout=5,
    )

    # 获取配置状态
    response = requests.get("http://127.0.0.1:8000/api/v1/config/status", timeout=5)

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["api_key_configured"] is True
    assert data["model_name"] == test_model
    assert "sk-test-s" in data["api_key_preview"]  # 验证前缀显示

    print("✅ 配置状态 API 测试通过")


def test_partial_config_update():
    """测试部分配置更新"""
    # 只更新模型名称
    test_model = "gpt-3.5-turbo"

    response = requests.post(
        "http://127.0.0.1:8000/api/v1/config/update",
        json={"model_name": test_model},
        timeout=5,
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "model_name" in data["updated_fields"]
    assert "api_key" not in data["updated_fields"]

    # 验证配置已更新
    status_response = requests.get(
        "http://127.0.0.1:8000/api/v1/config/status", timeout=5
    )
    status_data = status_response.json()
    assert status_data["model_name"] == test_model

    print("✅ 部分配置更新测试通过")


if __name__ == "__main__":
    print("开始测试配置 API...")
    print("\n测试 1: 配置更新 API")
    test_config_update_api()

    print("\n测试 2: 配置状态 API")
    test_config_status_api()

    print("\n测试 3: 部分配置更新")
    test_partial_config_update()

    print("\n✅ 所有测试通过！")
