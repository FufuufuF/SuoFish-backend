from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select
from src.db.models.model_config import ModelConfig

async def add_model_config(db: AsyncSession, model_config: ModelConfig) -> ModelConfig:
    db.add(model_config)
    await db.commit()
    await db.refresh(model_config)
    return model_config

async def get_model_configs_by_user_id(db: AsyncSession, user_id: int) -> List[ModelConfig]:
    result = await db.execute(select(ModelConfig).filter(ModelConfig.user_id == user_id))
    return result.scalars().all()