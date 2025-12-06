from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class LLMSettings(BaseSettings):
    """LLM 配置"""
    # 支持 DASHSCOPE_API_KEY 作为别名（兼容现有环境变量）
    api_key: str = Field(validation_alias="DASHSCOPE_API_KEY")
    base_url: str = Field(validation_alias="QWEN_BASE_URL")
    model_name: str = Field(default="qwen-plus", validation_alias="QWEN_MODEL_NAME")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class EmbeddingSettings(BaseSettings):
    """Embedding """
    api_key: str = Field(validation_alias="DASHSCOPE_API_KEY")
    base_url: str = Field(validation_alias="QWEN_BASE_URL")
    model_name: str = Field(default="text-embedding-v1", validation_alias="TONGYI_MODEL_NAME")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

