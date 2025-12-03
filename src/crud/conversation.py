from typing import List, Optional
from sqlalchemy.orm import Session

from src.db.models.conversation import Conversation


def create_conversation(db: Session, conversation: Conversation) -> Conversation:
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversations_by_user_id(db: Session, user_id: int) -> List[Conversation]:
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).all()


def update_conversation_name(db: Session, conversation_id: int, name: str) -> Optional[Conversation]:
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.name = name
        db.commit()
        db.refresh(conversation)
    return conversation


def delete_conversation_by_id(db: Session, conversation_id: int) -> bool:
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False


def update_conversation_summary(db: Session, conversation_id: int, summary: str) -> Optional[Conversation]:
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.summary = summary
        db.commit()
        db.refresh(conversation)
    return conversation

