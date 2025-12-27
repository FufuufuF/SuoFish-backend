from pydantic import BaseModel
from datetime import datetime

class UserResponse(BaseModel):
    """用户信息响应（不包含密码）"""
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
