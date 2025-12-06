# -*- coding: utf-8 -*-

"""
统一配置管理模块
提供一致的配置管理接口，支持环境变量和配置文件
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """通用配置基类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent

    DEBUG: bool = False
    
    # 数据库配置
    SQLITE_DB_NAME: str = "app.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TOKEN_TYPE: str = "bearer"
    
    # 服务配置
    SERVICE_NAME: str = "fastapi-service"
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SERVICE_PORT: int = 8000
    
    # 服务发现配置
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    
    @property
    def DATABASE_URL(self) -> str:
        """数据库URL"""
        return f"sqlite:///{self.BASE_DIR.joinpath(self.SQLITE_DB_NAME)}?characterEncoding=UTF-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    获取通用配置实例（带缓存）
    
    Returns:
        Settings: 配置实例
    """
    return Settings()


# 默认配置实例
settings = get_settings()