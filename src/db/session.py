from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.core.config import database as db_config

# 使用新的配置方式获取数据库 URL
SQLALCHEMY_DATABASE_URL = db_config.async_url

# 创建 SQLAlchemy 异步 Engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_recycle=3600  # 避免 MySQL 长时间不活动导致连接断开
)

# 创建 AsyncSessionLocal 类
# 每次请求都会创建的异步数据库会话（连接）
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

# 创建 Base 类
# 它是所有 ORM 模型的基础类
Base = declarative_base()
