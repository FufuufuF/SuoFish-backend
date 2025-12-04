from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """认证配置"""
    secret_key: str
    algorithm: str = "HS256"
    expiration_time: int = 3600  # 秒
    
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

