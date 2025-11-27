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