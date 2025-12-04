from functools import lru_cache
from .settings import Settings
from .database import DatabaseSettings
from .auth import AuthSettings
from .ai import LLMSettings, EmbeddingSettings
from .cors import CORSSettings


# 导出配置实例（带缓存）
@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


@lru_cache
def get_llm_settings() -> LLMSettings:
    return LLMSettings()


@lru_cache
def get_embedding_settings() -> EmbeddingSettings:
    return EmbeddingSettings()


@lru_cache
def get_cors_settings() -> CORSSettings:
    return CORSSettings()


# 便捷导出实例
settings = get_settings()
database = get_database_settings()
auth = get_auth_settings()
llm = get_llm_settings()
embedding = get_embedding_settings()
cors = get_cors_settings()

