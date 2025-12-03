from typing import List, Optional
from sqlalchemy.orm import Session

from src.db.models.message import Message


def create_message(db: Session, message: Message) -> Message:
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_messages_batch(db: Session, messages: List[Message]) -> List[Message]:
    db.add_all(messages)
    db.commit()
    for message in messages:
        db.refresh(message)
    return messages


def get_message_by_id(db: Session, message_id: int) -> Optional[Message]:
    return db.query(Message).filter(Message.id == message_id).first()


def get_messages_by_conversation_id(db: Session, conversation_id: int) -> List[Message]:
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

def get_K_messages_by_conversation_id(db: Session, conversation_id: int, k: int) -> List[Message]:
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(k).all()
    # 反转顺序，使消息按时间正序排列
    return list(reversed(messages))


def get_message_count_by_conversation_id(db: Session, conversation_id: int) -> int:
    """获取会话的消息总数"""
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).count()
