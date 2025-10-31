"""
启动Streamlit前端界面
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    from src.config import config

    app_path = str(project_root / "src" / "ui" / "app.py")

    print(f"🚀 启动Streamlit界面...")
    print(f"📍 地址: http://localhost:{config.STREAMLIT_PORT}")

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port",
        str(config.STREAMLIT_PORT),
        "--server.headless",
        "true",
    ]

    sys.exit(stcli.main())
