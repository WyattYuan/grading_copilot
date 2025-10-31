"""
启动FastAPI后端服务
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    from src.config import config

    print(f"🚀 启动FastAPI服务...")
    print(f"📍 地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"📖 API文档: http://{config.API_HOST}:{config.API_PORT}/docs")

    uvicorn.run(
        "src.api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True
    )
