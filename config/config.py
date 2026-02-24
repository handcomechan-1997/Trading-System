"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量 - 优先加载 secrets.env，然后加载 .env
base_dir = Path(__file__).resolve().parent.parent
secrets_file = base_dir / "secrets.env"
env_file = base_dir / ".env"

# 先加载 .env（通用配置）
if env_file.exists():
    load_dotenv(env_file)

# 再加载 secrets.env（会覆盖 .env 中的同名变量）
if secrets_file.exists():
    load_dotenv(secrets_file, override=True)

class Settings(BaseSettings):
    """应用配置"""
    
    # 项目路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # 数据源配置
    TUSHARE_TOKEN: Optional[str] = os.getenv("TUSHARE_TOKEN")
    AKSHARE_ENABLED: bool = os.getenv("AKSHARE_ENABLED", "true").lower() == "true"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/trade.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API服务配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 全局配置实例
settings = Settings()
