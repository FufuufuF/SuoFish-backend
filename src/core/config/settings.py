from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用基础配置"""
    app_name: str = "ChatBot"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略额外的环境变量
    )


@lru_cache
def get_settings() -> Settings:
    """缓存配置实例，避免重复读取"""
    return Settings()

