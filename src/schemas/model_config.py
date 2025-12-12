"""
模型配置相关的 Pydantic Schema

分层说明：
- Base: 包含所有共享的字段（用于复用）
- Create: 用于 POST 请求创建资源
- Update: 用于 PUT/PATCH 请求更新资源
- InDB: 表示数据库中的完整字段（包含 id、时间戳等）
- Response: 用于 API 响应（可以选择性隐藏某些字段如 api_key）
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ModelConfigBase(BaseModel):
    """模型配置基础字段 - 所有 schema 共享的字段"""
    model_name: str = Field(..., description="模型名称，如 gpt-4")
    display_name: str = Field(..., description="显示名称，用户友好的名称")
    base_url: str = Field(..., description="API 基础 URL")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(2048, gt=0, description="最大令牌数")


class ModelConfigCreate(ModelConfigBase):
    """创建模型配置的请求体"""
    api_key: str = Field(..., description="API 密钥")
    is_default: bool = Field(False, description="是否设为默认模型")


class ModelConfigUpdate(BaseModel):
    """更新模型配置的请求体 - 前端提交完整配置"""
    id: int = Field(..., description="模型配置 ID")
    model_name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    base_url: str = Field(..., description="API 基础 URL")
    api_key: str = Field(..., description="API 密钥")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(2048, gt=0, description="最大令牌数")
    is_default: Optional[bool] = Field(None, description="是否设为默认模型")


class ModelConfigDelete(BaseModel):
    """删除模型配置的请求体"""
    id: int = Field(..., description="要删除的模型配置 ID")


class ModelConfigInDB(ModelConfigBase):
    """数据库中的模型配置 - 完整字段"""
    id: int
    user_id: int
    api_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # 允许从 SQLAlchemy 模型创建
    }


class ModelConfigResponse(ModelConfigBase):
    """API 响应 - 不包含敏感信息的版本"""
    id: int
    user_id: int
    api_key: str  # 可以考虑脱敏：api_key: str = Field(..., description="API密钥（已脱敏）")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ModelConfigListResponse(BaseModel):
    """模型配置列表响应"""
    model_configs: list[ModelConfigResponse]
    default_model_id: Optional[int] = None

