"""
配置管理
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """全局配置"""

    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "qwen-plus")
    
    # 阿里云 DashScope 配置（通义千问）
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

    # API 配置
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Streamlit 配置
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # 并发配置
    GRADING_BATCH_SIZE: int = int(
        os.getenv("GRADING_BATCH_SIZE", "10")
    )  # 每批并发评分数量
    MAX_CONCURRENT_TASKS: int = int(
        os.getenv("MAX_CONCURRENT_TASKS", "50")
    )  # 最大并发任务数

    # 路径配置
    BASE_DIR: Path = Path(
        __file__
    ).parent.parent  # src/config.py -> src -> grading_copilot
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
