from pydantic import BaseModel

class LLMConfig(BaseModel):
    api_key: str
    base_url: str
    model_name: str

class MessageMetadata(BaseModel):
    llm_message_id: str
    user_message_id: str
    