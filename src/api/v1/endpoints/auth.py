from fastapi import APIRouter, Depends

from src.shcemas.api_response import APIResponse
from src.utils.authentic import get_current_user

router = APIRouter()

@router.get("/")
def auth(user_id: str = Depends(get_current_user)):
    try:
        # 使用 get_current_user 验证 token
        print(user_id)
        
        # 如果返回的是字典（错误情况），说明 token 无效
        if isinstance(user_id, dict):
            return APIResponse(**user_id)

        # Token 有效，返回成功
        return APIResponse(retcode=0, message="success", data=None)
    
    except Exception as e:
        # 处理其他异常
        return APIResponse(retcode=401, message=str(e), data=None)