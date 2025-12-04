from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# 2. 构造 SQLAlchemy 异步连接 URL
# 格式: mysql+aiomysql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 3. 创建 SQLAlchemy 异步 Engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_recycle=3600  # 避免 MySQL 长时间不活动导致连接断开
)

# 4. 创建 AsyncSessionLocal 类
# 每次请求都会创建的异步数据库会话（连接）
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

# 5. 创建 Base 类
# 它是所有 ORM 模型的基础类
Base = declarative_base()
