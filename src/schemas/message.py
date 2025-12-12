"""
消息（Message）相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """消息基础字段"""
    content: str = Field(..., description="消息内容")
    role: MessageRole = Field(..., description="消息角色")


class MessageCreate(MessageBase):
    """
    创建消息的请求体
    
    通常由内部服务调用，不直接暴露给前端
    前端应该使用 Chat 接口
    """
    conversation_id: int = Field(..., description="所属会话 ID")


class MessageInDB(MessageBase):
    """数据库中的完整消息数据"""
    id: int
    conversation_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MessageResponse(MessageBase):
    """API 返回的消息数据"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: list[MessageResponse]
    total: int
    conversation_id: int

