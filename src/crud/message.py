from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.models.message import Message


async def create_message(db: AsyncSession, message: Message) -> Message:
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def create_messages_batch(db: AsyncSession, messages: List[Message]) -> List[Message]:
    db.add_all(messages)
    await db.commit()
    for message in messages:
        await db.refresh(message)
    return messages


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
    result = await db.execute(select(Message).filter(Message.id == message_id))
    return result.scalar_one_or_none()


async def get_messages_by_conversation_id(db: AsyncSession, conversation_id: int) -> List[Message]:
    result = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def get_K_messages_by_conversation_id(db: AsyncSession, conversation_id: int, k: int) -> List[Message]:
    result = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(k)
    )
    messages = list(result.scalars().all())
    # 反转顺序，使消息按时间正序排列
    return list(reversed(messages))


async def get_message_count_by_conversation_id(db: AsyncSession, conversation_id: int) -> int:
    """获取会话的消息总数"""
    result = await db.execute(
        select(func.count()).select_from(Message).filter(Message.conversation_id == conversation_id)
    )
    return result.scalar() or 0
