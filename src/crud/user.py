from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.model_config import ModelConfig
from src.db.models.user import User


async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_user_hash_password(db: AsyncSession, email: str) -> Optional[str]:
    user = await get_user_by_email(db, email)
    return user.password if user else None

async def get_user_default_model_config_id(db: AsyncSession, user_id: int) -> Optional[int]:
    user = await get_user_by_id(db, user_id)
    return user.default_model_config_id if user else None

async def get_user_default_model_config(db: AsyncSession, user_id: int) -> Optional[ModelConfig]:
    user = await get_user_by_id(db, user_id)
    if user is None or user.default_model_config_id is None:
        return None
    result = await db.execute(select(ModelConfig).filter(ModelConfig.id == user.default_model_config_id))
    return result.scalar_one_or_none()

async def set_user_default_model_config(db: AsyncSession, user_id: int, model_config_id: int):
    user = await get_user_by_id(db, user_id)
    user.default_model_config_id = model_config_id
    await db.commit()
    await db.refresh(user)
    return user