from pydantic import BaseModel

class LLMConfig(BaseModel):
    api_key: str
    base_url: str
    model_name: str

class ChatMetadata(BaseModel):
    llm_message_id: int
    user_message_id: int
    conversation_id: int
    