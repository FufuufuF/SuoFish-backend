from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.conversation import Conversation


async def create_conversation(db: AsyncSession, conversation: Conversation) -> Conversation:
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation_by_id(db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
    result = await db.execute(select(Conversation).filter(Conversation.id == conversation_id))
    return result.scalar_one_or_none()


async def get_conversations_by_user_id(db: AsyncSession, user_id: int) -> List[Conversation]:
    result = await db.execute(
        select(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_conversation_name(db: AsyncSession, conversation_id: int, name: str) -> Optional[Conversation]:
    conversation = await get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.name = name
        await db.commit()
        await db.refresh(conversation)
    return conversation


async def delete_conversation_by_id(db: AsyncSession, conversation_id: int) -> bool:
    conversation = await get_conversation_by_id(db, conversation_id)
    if conversation:
        await db.delete(conversation)
        await db.commit()
        return True
    return False


async def update_conversation_summary(db: AsyncSession, conversation_id: int, summary: str) -> Optional[Conversation]:
    conversation = await get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.summary = summary
        await db.commit()
        await db.refresh(conversation)
    return conversation
