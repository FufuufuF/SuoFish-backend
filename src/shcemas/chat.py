from pydantic import BaseModel

class Chat(BaseModel):
    user_message: str
    session_id: str
