"""
认证相关的 Pydantic Schema

包含登录、注册等认证操作的请求和响应
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class UserBase(BaseModel):
    """用户基础字段"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class UserRegister(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=6, max_length=100, description="密码（至少6位）")


class UserLogin(BaseModel):
    """用户登录请求"""
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=4, max_length=100, description="密码")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class UserInDB(UserBase):
    """数据库中的用户数据"""
    id: int
    password: str  # 这是 hash 后的密码
    created_at: datetime
    default_model_config_id: int | None = None

    model_config = {
        "from_attributes": True
    }


class UserResponse(BaseModel):
    """用户信息响应（不包含密码）"""
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    """登录成功后的 Token 响应"""
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")

