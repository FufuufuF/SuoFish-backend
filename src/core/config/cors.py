from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class CORSSettings(BaseSettings):
    """CORS 跨域配置"""
    origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    @field_validator("origins", "allow_methods", "allow_headers", mode="before")
    @classmethod
    def split_string(cls, v: Union[str, List[str]]) -> List[str]:
        """将逗号分隔的字符串转换为列表"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

