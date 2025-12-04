"""
ConversationFile CRUD 操作
"""
from typing import Optional
from sqlalchemy.orm import Session

from src.db.models.conversation_file import ConversationFile


def add_file(
    db: Session,
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
    db.commit()
    db.refresh(conversation_file)
    return conversation_file

def get_file_by_id(db: Session, file_id: int) -> Optional[ConversationFile]:
    """根据 ID 获取文件记录"""
    return db.query(ConversationFile).filter(ConversationFile.id == file_id).first()


def get_files_by_conversation(db: Session, conversation_id: int) -> list[ConversationFile]:
    """获取会话的所有文件"""
    return db.query(ConversationFile).filter(
        ConversationFile.conversation_id == conversation_id
    ).order_by(ConversationFile.created_at.desc()).all()


def get_parsed_files_by_conversation(db: Session, conversation_id: int) -> list[ConversationFile]:
    """获取会话中已解析的文件"""
    return db.query(ConversationFile).filter(
        ConversationFile.conversation_id == conversation_id,
        ConversationFile.status == "parsed"
    ).order_by(ConversationFile.created_at.desc()).all()


def update_file_status(db: Session, file_id: int, status: str) -> Optional[ConversationFile]:
    """更新文件状态"""
    file = get_file_by_id(db, file_id)
    if file:
        file.status = status
        db.commit()
        db.refresh(file)
    return file


def delete_file(db: Session, file_id: int) -> bool:
    """删除文件记录"""
    file = get_file_by_id(db, file_id)
    if file:
        db.delete(file)
        db.commit()
        return True
    return False


def count_files_by_conversation(db: Session, conversation_id: int) -> int:
    """统计会话的文件数量"""
    return db.query(ConversationFile).filter(
        ConversationFile.conversation_id == conversation_id
    ).count()

