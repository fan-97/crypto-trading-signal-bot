from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv('BINANCE_API_SECRET',"")
    enable_ai_analysis: bool = os.getenv('ENABLE_AI_ANALYSIS',"")
    klines_limit: int = os.getenv('KLINES_LIMIT',250)
    ai_confidence_threshold: float = os.getenv('AI_CONFIDENCE_THRESHOLD', 80)

    # Email Settings
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    sender_email: str = os.getenv("SENDER_EMAIL", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    receiver_emails: str = os.getenv("RECEIVER_EMAILS", "")
    
    # Telegram Settings
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_ids: str = os.getenv("TELEGRAM_CHAT_IDS", "")

    # Application Settings
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./crypto.db")

    # Redis Settings
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # Cache Settings
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))  # 默认5分钟
    klines_cache_ttl: int = int(os.getenv("KLINES_CACHE_TTL", "60"))  # 默认1分钟
    ticker_cache_ttl: int = int(os.getenv("TICKER_CACHE_TTL", "10"))  # 默认10秒

    # Model Settings
    model_path: str = os.getenv("MODEL_PATH", "./models")
    prediction_threshold: float = float(os.getenv("PREDICTION_THRESHOLD", "0.7"))

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 