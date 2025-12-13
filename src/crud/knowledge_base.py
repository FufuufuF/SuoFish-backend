from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.knowledge_base import KnowledgeBase

async def create_knowledge_base(db: AsyncSession, knowledge_base: KnowledgeBase) -> KnowledgeBase:
    db.add(knowledge_base)
    await db.commit()
    await db.refresh(knowledge_base)
    return knowledge_base

async def get_knowledge_base_by_user_id(db: AsyncSession, user_id: int) -> List[KnowledgeBase]:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.user_id == user_id))
    return result.scalars().all()

async def get_knowledge_base_by_id(db: AsyncSession, id: int) -> KnowledgeBase:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == id))
    return result.scalar_one_or_none()

async def delete_knowledge_base(db: AsyncSession, id: int) -> bool:
    knowledge_base = await get_knowledge_base_by_id(db, id)
    if knowledge_base is None:
        return False
    await db.delete(knowledge_base)
    await db.commit()
    return True