from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.db.session import Base


class ModelConfig(Base):
    """
    模型配置 - 每个用户可以有多个模型配置
    """
    __tablename__ = "model_config"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    model_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    temperature = Column(Float, nullable=False)
    max_tokens = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # 关联关系 - 显式指定外键，因为 User 和 ModelConfig 之间有两个外键路径
    user = relationship("User", back_populates="model_configs", foreign_keys=[user_id])

    