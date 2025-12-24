import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AI 配置
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai 或 gemini
    ENABLE_AI_POLISH = os.getenv("ENABLE_AI_POLISH", "true").lower() == "true"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # 支持中转 API
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Whisper
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    
    # 飞书
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
    FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    FEISHU_BITABLE_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID")
    
    # 系统配置
    DOWNLOAD_PATH = Path(os.getenv("DOWNLOAD_PATH", "./downloads"))
    OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "./outputs"))
    COOKIES_FILE = os.getenv("COOKIES_FILE", "./cookies.txt")
    
    # 系统
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def ensure_dirs(cls):
        cls.DOWNLOAD_PATH.mkdir(exist_ok=True)
        cls.OUTPUT_PATH.mkdir(exist_ok=True)

config = Config()
config.ensure_dirs()
