from sqlalchemy import Column, String, Integer

from src.db.session import Base

class Messages(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    role = Column(String(20), index=True)
    content = Column(String, index=True)