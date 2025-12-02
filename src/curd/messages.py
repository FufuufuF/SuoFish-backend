from typing import List
from sqlalchemy.orm import Session

from src.db.models.messages import Messages

def create_message(db: Session, message: Messages):
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def create_message_batch(db: Session, messages: List[Messages]):
    db.add_all(messages)
    db.commit()
    for message in messages:
        db.refresh(message)
    return messages

def get_message_by_id(db: Session, message_id: int):
    return db.query(Messages).filter(Messages.message_id == message_id).first()
    