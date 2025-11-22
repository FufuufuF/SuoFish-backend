from sqlalchemy import Column, String, Integer

from src.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

