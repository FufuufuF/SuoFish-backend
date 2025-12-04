from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 异步依赖项：
    - 在请求开始时创建异步数据库会话
    - 在请求完成后关闭数据库会话（无论成功或失败）
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    异步上下文管理器：用于后台任务等非 FastAPI 依赖场景
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
