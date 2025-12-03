from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.db.session import Base


class Conversation(Base):
    __tablename__ = "conversation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(100), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    summary = Column(Text, nullable=True)
    
    # 关联关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at", cascade="all, delete-orphan")

