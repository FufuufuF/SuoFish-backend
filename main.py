from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import router as v1_router
from src.db.session import Base, engine
from src.core.config import cors as cors_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时创建表"""
    # 启动时：使用异步引擎创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时：可以在这里添加清理逻辑


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)

app.include_router(v1_router, prefix="/api/v1")
