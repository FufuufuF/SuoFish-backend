from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ConversationLogRequest(BaseModel):
    conversation_id: int = Field(..., description="会话ID")

class ConversationLogResponse(BaseModel):
    id: int = Field(..., description="会话日志回合ID")
    session_id: int = Field(..., description="会话日志会话ID")
    round_number: int = Field(..., description="回合编号")
    user_message: str = Field(..., description="用户消息")
    assistant_message: str = Field(..., description="助手消息")
    files_result: Optional[dict] = Field(None, description="文件上传结果")
    rag_results: Optional[dict] = Field(None, description="RAG检索结果")
    error: Optional[str] = Field(None, description="错误信息")
    save_error: Optional[str] = Field(None, description="保存错误")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {
        "from_attributes": True
    }
    