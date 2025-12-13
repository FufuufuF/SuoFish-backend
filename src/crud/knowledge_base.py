from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.knowledge_base import KnowledgeBase


async def create_knowledge_base(
    db: AsyncSession, 
    knowledge_base: KnowledgeBase
) -> KnowledgeBase:
    """创建知识库"""
    db.add(knowledge_base)
    await db.commit()
    await db.refresh(knowledge_base)
    return knowledge_base


async def get_knowledge_bases_by_user(
    db: AsyncSession, 
    user_id: int
) -> List[KnowledgeBase]:
    """获取用户的所有知识库"""
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.user_id == user_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    return list(result.scalars().all())


async def get_knowledge_base_by_id(
    db: AsyncSession, 
    kb_id: int
) -> Optional[KnowledgeBase]:
    """根据 ID 获取知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    return result.scalar_one_or_none()


async def delete_knowledge_base(db: AsyncSession, kb_id: int) -> bool:
    """删除知识库"""
    knowledge_base = await get_knowledge_base_by_id(db, kb_id)
    if knowledge_base is None:
        return False
    await db.delete(knowledge_base)
    await db.commit()
    return True