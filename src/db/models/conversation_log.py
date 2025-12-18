from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.session import Base

class ConversationLogSession(Base):
    """
    会话日志会话表 - 存储会话中的日志会话信息
    """
    __tablename__ = "conversation_log_session"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    total_rounds = Column(Integer, default=0)
    has_errors = Column(Boolean, default=False, index=True)

    rounds = relationship("ConversationLogRound", back_populates="session", cascade="all, delete-orphan")

class ConversationLogRound(Base):
    """
    会话日志回合表 - 存储会话中的日志回合信息
    """
    __tablename__ = "conversation_log_round"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("conversation_log_session.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)  # 第几轮对话
    
    # 一轮对话包含的所有信息
    user_message = Column(Text, nullable=False)           # 用户说的话
    assistant_message = Column(Text, nullable=False)      # 助手的回复
    files_result = Column(JSON, nullable=True)            # 文件上传结果（JSON 格式）
    rag_results = Column(JSON, nullable=True)             # RAG 检索结果（JSON 格式）
    error = Column(Text, nullable=True)                   # 错误信息（可选）
    save_error = Column(Text, nullable=True)              # 保存错误（可选）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # 创建时间

    session = relationship("ConversationLogSession", back_populates="rounds")