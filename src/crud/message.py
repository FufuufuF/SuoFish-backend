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

