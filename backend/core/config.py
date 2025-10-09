import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:yjakgl11@localhost/wenke_ai_db")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 一周
    
    # 认证配置
    ENABLE_AUTH: bool = True  # 启用认证
    
    class Config:
        env_file = ".env"

settings = Settings()