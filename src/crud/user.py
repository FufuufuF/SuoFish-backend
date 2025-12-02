from typing import Optional
from sqlalchemy.orm import Session

from src.db.models.user import User


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_hash_password(db: Session, email: str) -> Optional[str]:
    user = get_user_by_email(db, email)
    return user.password if user else None

