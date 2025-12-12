"""
聊天相关的 Pydantic Schema

注意：
- ConversationResponse 已迁移至 src/schemas/conversation.py
- MessageResponse 已迁移至 src/schemas/message.py
- 这里只保留聊天请求和实时通信相关的 schema
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    聊天请求
    
    前端发送的聊天消息
    """
    user_message: str = Field(..., min_length=1, description="用户消息内容")
    conversation_id: Optional[int] = Field(None, description="会话 ID，如果为 None 则创建新会话")
    model_config_id: Optional[int] = Field(None, description="使用的模型配置 ID，如果为 None 则使用默认配置")


class ChatResponse(BaseModel):
    """
    聊天响应
    
    包含 AI 回复和相关元数据
    """
    assistant_message: str = Field(..., description="AI 助手的回复")
    metadata: "ChatMetadata" = Field(..., description="聊天元数据")


class ChatMetadata(BaseModel):
    """
    聊天元数据
    
    包含消息 ID、会话信息等
    """
    llm_message_id: int = Field(..., description="AI 消息 ID")
    user_message_id: int = Field(..., description="用户消息 ID")
    conversation_id: int = Field(..., description="会话 ID")
    conversation_name: str = Field(..., description="会话名称")
    created_at: int = Field(..., description="创建时间戳")
    updated_at: int = Field(..., description="更新时间戳")


class StreamChunk(BaseModel):
    """
    流式响应的数据块
    
    用于 SSE (Server-Sent Events) 流式传输
    """
    content: str = Field(..., description="增量内容")
    is_final: bool = Field(False, description="是否是最后一块")
    metadata: Optional[ChatMetadata] = Field(None, description="最后一块时包含元数据")


