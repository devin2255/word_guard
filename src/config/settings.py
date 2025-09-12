"""应用配置"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 加载 .env 文件
load_dotenv(dotenv_path="app/config/product.env")


class Settings(BaseSettings):
    """应用设置"""
    
    app_name: str = os.getenv("APP_NAME", "御言内容风控系统")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "mysql://root:2255@127.0.0.1:3306/yuyan")
    debug_mode: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    port: int = int(os.getenv("PORT", "9000"))
    secret_key: str = os.getenv("SECRET_KEY", "my_secret_key_123")
    
    class Config:
        env_file = "app/config/product.env"


settings = Settings()