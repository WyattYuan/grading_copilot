"""
配置管理
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置"""

    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "qwen-plus")

    # API 配置
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Streamlit 配置
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    EXAMPLES_DIR: Path = DATA_DIR / "examples"

    @classmethod
    def ensure_dirs(cls):
        """确保必要的目录存在"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.UPLOADS_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        cls.EXAMPLES_DIR.mkdir(exist_ok=True)


config = Config()
