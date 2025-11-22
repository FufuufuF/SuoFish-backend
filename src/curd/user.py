from sqlalchemy.orm import Session

from src.db.models.user import User

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def get_user_hash_password(db: Session, email: str):
    return db.query(User).filter(User.email == email).first().password
