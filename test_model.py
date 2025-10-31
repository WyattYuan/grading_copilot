"""
测试通义千问模型可用性
"""

from langchain_community.chat_models.tongyi import ChatTongyi
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()

# 常见的通义千问模型列表
models_to_test = [
    "qwen-turbo",
    "qwen-plus",
    "qwen-max",
    "qwen-max-longcontext",
    "qwen2-72b-instruct",
    "qwen2-57b-a14b-instruct",
]

api_key = os.getenv("DASHSCOPE_API_KEY", "")

print("🔍 测试通义千问模型可用性...\n")

for model_name in models_to_test:
    try:
        llm = ChatTongyi(
            model=model_name,
            api_key=SecretStr(api_key),
        )

        # 尝试简单调用
        response = llm.invoke("你好")
        print(f"✅ {model_name}: 可用")
        print(f"   响应: {response.content[:50]}...\n")

    except Exception as e:
        error_msg = str(e)
        if "Model not exist" in error_msg:
            print(f"❌ {model_name}: 模型不存在\n")
        else:
            print(f"⚠️  {model_name}: {error_msg}\n")

print("\n建议: 选择标记为 ✅ 的模型更新到 .env 文件中")
