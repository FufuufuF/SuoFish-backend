from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Request

from src.core.config import auth as auth_config


def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    创建 JWT 访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间（秒），默认使用配置中的过期时间
    """
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = auth_config.expiration_time
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth_config.secret_key, algorithm=auth_config.algorithm)
    return encoded_jwt


def get_current_user(request: Request):
    """
    从请求中获取当前用户
    
    Returns:
        int: 用户 ID（成功时）
        dict: 错误信息（失败时）
    """
    token = request.cookies.get("access_token")

    if not token:
        return {
            'retcode': 401,
            'message': 'Unauthorized',
            'data': None,
        }

    try:
        payload = jwt.decode(token, auth_config.secret_key, algorithms=[auth_config.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            return {
                'retcode': 401,
                'message': 'Invalid token',
                'data': None,
            }
        
        return int(user_id)
    except jwt.ExpiredSignatureError:
        return {
            'retcode': 401,
            'message': 'Token expired',
            'data': None,
        }
    except JWTError:
        return {
            'retcode': 401,
            'message': 'Invalid token',
            'data': None,
        }
