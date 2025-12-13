"""
KnowledgeBaseFile CRUD 操作
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.models.knowledge_base_file import KnowledgeBaseFile


async def add_file(
    db: AsyncSession,
    knowledge_base_id: int,
    file_name: str,
    file_type: str,
    file_size: int,
    file_path: str,
    file_content: Optional[str] = None
) -> KnowledgeBaseFile:
    """添加知识库文件记录"""
    kb_file = KnowledgeBaseFile(
        knowledge_base_id=knowledge_base_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        file_path=file_path,
        file_content=file_content
    )
    db.add(kb_file)
    await db.commit()
    await db.refresh(kb_file)
    return kb_file


async def get_file_by_id(
    db: AsyncSession, 
    file_id: int
) -> Optional[KnowledgeBaseFile]:
    """根据 ID 获取文件记录"""
    result = await db.execute(
        select(KnowledgeBaseFile).filter(KnowledgeBaseFile.id == file_id)
    )
    return result.scalar_one_or_none()


async def get_files_by_knowledge_base(
    db: AsyncSession, 
    knowledge_base_id: int
) -> List[KnowledgeBaseFile]:
    """获取知识库的所有文件"""
    result = await db.execute(
        select(KnowledgeBaseFile)
        .filter(KnowledgeBaseFile.knowledge_base_id == knowledge_base_id)
        .order_by(KnowledgeBaseFile.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_file(db: AsyncSession, file_id: int) -> bool:
    """删除文件记录"""
    file = await get_file_by_id(db, file_id)
    if file:
        await db.delete(file)
        await db.commit()
        return True
    return False


async def delete_files_by_knowledge_base(
    db: AsyncSession, 
    knowledge_base_id: int
) -> bool:
    """删除知识库的所有文件记录"""
    try:
        files = await get_files_by_knowledge_base(db, knowledge_base_id)
        for file in files:
            await db.delete(file)
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False


async def count_files_by_knowledge_base(
    db: AsyncSession, 
    knowledge_base_id: int
) -> int:
    """统计知识库的文件数量"""
    result = await db.execute(
        select(func.count())
        .select_from(KnowledgeBaseFile)
        .filter(KnowledgeBaseFile.knowledge_base_id == knowledge_base_id)
    )
    return result.scalar() or 0

