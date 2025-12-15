from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus


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


async def update_knowledge_base_status(
    db: AsyncSession,
    kb_id: int,
    status: KnowledgeBaseStatus
) -> Optional[KnowledgeBase]:
    """更新知识库状态"""
    kb = await get_knowledge_base_by_id(db, kb_id)
    if not kb:
        return None
    
    kb.status = status.value
    await db.commit()
    await db.refresh(kb)
    return kb


async def add_file_to_knowledge_base(
    db: AsyncSession,
    kb_id: int,
    file_id: int,
    file_name: str
) -> Optional[KnowledgeBase]:
    """添加文件到知识库的文件列表"""
    # TODO: 添加RAG逻辑
    kb = await get_knowledge_base_by_id(db, kb_id)
    if not kb:
        return None
    
    if kb.file_list is None:
        kb.file_list = []
    
    # 检查文件是否已存在
    if not any(f.get("file_id") == file_id for f in kb.file_list):
        kb.file_list.append({
            "file_id": file_id,
            "file_name": file_name
        })
        await db.commit()
        await db.refresh(kb)
    
    return kb


async def remove_file_from_knowledge_base(
    db: AsyncSession,
    kb_id: int,
    file_id: int
) -> Optional[KnowledgeBase]:
    """从知识库的文件列表中移除文件"""
    kb = await get_knowledge_base_by_id(db, kb_id)
    if not kb:
        return None
    
    if kb.file_list:
        kb.file_list = [f for f in kb.file_list if f.get("file_id") != file_id]
        await db.commit()
        await db.refresh(kb)
    
    return kb


async def update_knowledge_base_file_list(
    db: AsyncSession,
    kb_id: int,
    file_list: List[Dict[str, Any]]
) -> Optional[KnowledgeBase]:
    """更新知识库的完整文件列表"""
    kb = await get_knowledge_base_by_id(db, kb_id)
    if not kb:
        return None
    
    kb.file_list = file_list
    await db.commit()
    await db.refresh(kb)
    return kb