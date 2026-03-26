from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """统一项目配置入口。

    这里同时服务现有核心流水线、重建后的后端，以及内部调试台。
    """

    ROOT_DIR: Final[Path] = Path(__file__).resolve().parents[1]

    # AI 配置
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    ENABLE_AI_POLISH: bool = _to_bool(os.getenv("ENABLE_AI_POLISH"), default=True)
    AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", "180"))

    KIMI_API_KEY: str | None = os.getenv("KIMI_API_KEY")
    KIMI_BASE_URL: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5.4")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://code.rayinai.com/v1")

    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # 飞书配置
    FEISHU_APP_ID: str | None = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET: str | None = os.getenv("FEISHU_APP_SECRET")
    FEISHU_BITABLE_APP_TOKEN: str | None = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    FEISHU_BITABLE_TABLE_ID: str | None = os.getenv("FEISHU_BITABLE_TABLE_ID")

    # 调度与后台配置
    AUTO_START_SCHEDULER: bool = _to_bool(os.getenv("AUTO_START_SCHEDULER"))
    SCHEDULER_CHECK_INTERVAL: int = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "300"))
    DB_SCHEDULER_BATCH_SIZE: int = int(os.getenv("DB_SCHEDULER_BATCH_SIZE", "10"))
    DB_SCHEDULER_RECOVER_TIMEOUT: int = int(os.getenv("DB_SCHEDULER_RECOVER_TIMEOUT", "3600"))

    # 后端配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(ROOT_DIR / 'local_dev.sqlite3').as_posix()}",
    )
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    # 默认联调口径统一到 8002，避免前后端各自回落到旧端口导致“看似可用、实际断连”
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8002"))
    JWT_SECRET: str = os.getenv("JWT_SECRET", "local-dev-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))
    API_BASE_URL: str = os.getenv("API_BASE_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")
    CLEANUP_DAYS_DEFAULT: int = int(os.getenv("CLEANUP_DAYS_DEFAULT", "30"))

    # 路径配置
    DOWNLOAD_PATH: Path = Path(os.getenv("DOWNLOAD_PATH", str(ROOT_DIR / "downloads")))
    OUTPUT_PATH: Path = Path(os.getenv("OUTPUT_PATH", str(ROOT_DIR / "outputs")))
    LOG_PATH: Path = Path(os.getenv("LOG_PATH", str(ROOT_DIR / "logs")))
    COOKIES_FILE: str = os.getenv("COOKIES_FILE", str(ROOT_DIR / "cookies.txt"))

    # 通用配置
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    @classmethod
    def ensure_dirs(cls) -> None:
        """确保运行期目录存在。"""

        for path in (cls.DOWNLOAD_PATH, cls.OUTPUT_PATH, cls.LOG_PATH):
            path.mkdir(parents=True, exist_ok=True)


config = Config()
config.ensure_dirs()
