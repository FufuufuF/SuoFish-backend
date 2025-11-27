from sqlalchemy.orm import Session

from src.db.models.users import Users

def create_user(db: Session, user: Users):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_user_by_id(db: Session, id: int):
    return db.query(Users).filter(Users.id == id).first()

def get_user_hash_password(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first().password
