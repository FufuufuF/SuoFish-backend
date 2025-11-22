from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# 2. 构造 SQLAlchemy 连接 URL
# 格式: mysql+pymysql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 3. 创建 SQLAlchemy Engine
# 配置 echo=True 可以看到生成的 SQL 语句，调试时有用
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_recycle=3600 # 避免 MySQL 长时间不活动导致连接断开
)

# 4. 创建 SessionLocal 类
# 每次请求都会创建的数据库会话（连接）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 创建 Base 类
# 它是所有 ORM 模型的基础类
Base = declarative_base()
