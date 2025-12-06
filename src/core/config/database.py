from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    host: str
    port: int = 3306
    name: str
    user: str
    password: str
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",  # 环境变量前缀：DB_HOST, DB_PORT...
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    @property
    def async_url(self) -> str:
        """异步数据库连接 URL"""
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """同步数据库连接 URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class ChromaSettings(BaseSettings):
    """Chroma 向量数据库配置"""
    path: str = "./chroma_data"  # 默认持久化路径
    collection_name: str = "documents"  # 默认集合名称
    
    model_config = SettingsConfigDict(
        env_prefix="CHROMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# 创建配置单例
chroma_settings = ChromaSettings()