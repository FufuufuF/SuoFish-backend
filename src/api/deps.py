from contextlib import asynccontextmanager
from src.db.session import SessionLocal

def get_db():
    """
    FastAPI 依赖项：
    - 在请求开始时创建数据库会话
    - 在请求完成后关闭数据库会话（无论成功或失败）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_db_context():
    """
    异步上下文管理器：用于后台任务等非 FastAPI 依赖场景
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()