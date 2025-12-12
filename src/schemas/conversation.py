"""
会话（Conversation）相关的 Pydantic Schema

按照分层设计模式组织：
- Base: 共享的核心字段
- Create: 用于创建会话
- Update: 用于更新会话
- InDB: 数据库完整字段
- Response: API 响应
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConversationBase(BaseModel):
    """会话基础字段"""
    name: str = Field(default="New Chat", max_length=100, description="会话名称")


class ConversationCreate(ConversationBase):
    """
    创建会话的请求体
    
    注意：会话创建时通常只需要名称，user_id 从 token 中获取
    """
    pass


class ConversationUpdate(BaseModel):
    """
    更新会话的请求体
    
    所有字段都是可选的，支持部分更新
    """
    name: Optional[str] = Field(None, max_length=100, description="会话名称")
    summary: Optional[str] = Field(None, description="会话摘要")


class ConversationInDB(ConversationBase):
    """数据库中的完整会话数据"""
    id: int
    user_id: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationResponse(ConversationBase):
    """
    API 返回的会话数据
    
    不包含 user_id（因为是当前用户自己的会话）
    """
    id: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationWithMessagesResponse(ConversationResponse):
    """
    包含消息的会话响应（用于详情页）
    """
    # 这里可以添加消息列表，避免循环导入可以用 TYPE_CHECKING
    message_count: int = Field(0, description="消息数量")
    file_count: int = Field(0, description="关联文件数量")


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    conversations: list[ConversationResponse]
    total: int

