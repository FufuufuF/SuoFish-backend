from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.db.session import Base


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 默认模型配置（一对一，保证每个用户只有一个默认配置）
    default_model_config_id = Column(Integer, ForeignKey("model_config.id"), nullable=True)
    
    # 关联关系
    conversations = relationship("Conversation", back_populates="user")
    model_configs = relationship("ModelConfig", back_populates="user", foreign_keys="ModelConfig.user_id")
    default_model_config = relationship("ModelConfig", foreign_keys=[default_model_config_id])
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")
