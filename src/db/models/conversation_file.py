from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.db.session import Base


class ConversationFile(Base):
    """
    会话文件表 - 存储用户在会话中上传的文件信息
    """
    __tablename__ = "conversation_file"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 文件基本信息
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(String(20), nullable=False, comment="文件类型: docx/pptx/xlsx/json/md/txt")
    file_size = Column(BigInteger, nullable=False, comment="文件大小（字节）")
    storage_path = Column(String(500), nullable=False, comment="存储路径")
    
    # 状态管理
    status = Column(String(20), nullable=False, default="uploaded", comment="状态: uploaded/processing/parsed/failed")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    conversation = relationship("Conversation", back_populates="files")
    user = relationship("User")
