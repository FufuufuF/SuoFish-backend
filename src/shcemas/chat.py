from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Chat(BaseModel):
    user_message: str
    conversation_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # 允许从 SQLAlchemy 模型创建
    }

class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True  # 允许从 SQLAlchemy 模型创建
    }
