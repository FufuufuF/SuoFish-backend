"""
ConversationFile CRUD 操作
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.models.conversation_file import ConversationFile


async def add_file(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    file_name: str,
    file_type: str,
    file_size: int,
    storage_path: str,
    status: str = "uploaded"
) -> ConversationFile:
    """添加文件记录"""
    conversation_file = ConversationFile(
        conversation_id=conversation_id,
        user_id=user_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
        status=status
    )
    db.add(conversation_file)
    await db.commit()
    await db.refresh(conversation_file)
    return conversation_file


async def get_file_by_id(db: AsyncSession, file_id: int) -> Optional[ConversationFile]:
    """根据 ID 获取文件记录"""
    result = await db.execute(select(ConversationFile).filter(ConversationFile.id == file_id))
    return result.scalar_one_or_none()


async def get_files_by_conversation(db: AsyncSession, conversation_id: int) -> list[ConversationFile]:
    """获取会话的所有文件"""
    result = await db.execute(
        select(ConversationFile)
        .filter(ConversationFile.conversation_id == conversation_id)
        .order_by(ConversationFile.created_at.desc())
    )
    return list(result.scalars().all())


async def get_parsed_files_by_conversation(db: AsyncSession, conversation_id: int) -> list[ConversationFile]:
    """获取会话中已解析的文件"""
    result = await db.execute(
        select(ConversationFile)
        .filter(
            ConversationFile.conversation_id == conversation_id,
            ConversationFile.status == "parsed"
        )
        .order_by(ConversationFile.created_at.desc())
    )
    return list(result.scalars().all())


async def update_file_status(db: AsyncSession, file_id: int, status: str) -> Optional[ConversationFile]:
    """更新文件状态"""
    file = await get_file_by_id(db, file_id)
    if file:
        file.status = status
        await db.commit()
        await db.refresh(file)
    return file


async def delete_file(db: AsyncSession, file_id: int) -> bool:
    """删除文件记录"""
    file = await get_file_by_id(db, file_id)
    if file:
        await db.delete(file)
        await db.commit()
        return True
    return False


async def count_files_by_conversation(db: AsyncSession, conversation_id: int) -> int:
    """统计会话的文件数量"""
    result = await db.execute(
        select(func.count()).select_from(ConversationFile).filter(ConversationFile.conversation_id == conversation_id)
    )
    return result.scalar() or 0
