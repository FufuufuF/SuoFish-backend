from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Request

from src.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME

def create_access_token(data: dict, expires_delta: Optional[timedelta] = JWT_EXPIRATION_TIME):
    to_encode = data.copy()
    expires_delta = timedelta(seconds=expires_delta)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        return {
            'retcode': 401,
            'message': 'Unauthorized',
            'data': None,
        }

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return {
                'retcode': 401,
                'message': 'Invalid token',
                'data': None,
            }
        
        return user_id
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