from pydantic import BaseModel
from datetime import datetime
class ModelConfigResponse(BaseModel):
    id: int
    user_id: int
    model_name: str
    display_name: str
    base_url: str
    api_key: str
    temperature: float
    max_tokens: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # 允许从 SQLAlchemy 模型创建
    }

class ChatMetadata(BaseModel):
    llm_message_id: int
    user_message_id: int
    conversation_id: int
    conversation_name: str
    created_at: int
    updated_at: int

