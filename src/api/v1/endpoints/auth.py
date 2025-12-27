from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from src.schemas.api_response import APIResponse
from src.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from src.db.models.user import User
from src.crud.user import create_user, get_user_by_email, get_user_hash_password
from src.api.deps import get_db
from src.utils.authentic import create_access_token, get_current_user

router = APIRouter()

async def verify_password(db: AsyncSession, email: str, login_password: str) -> bool:
    hashed_password = await get_user_hash_password(db, email)
    if not hashed_password:
        return False
    return bcrypt.checkpw(login_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/sign-up")
async def sign_up(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, user_data.email)
    if user:
        return APIResponse(retcode=400, message="Email already registered")
    user_data.password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    user = User(**user_data.model_dump())
    await create_user(db, user)
    return APIResponse(retcode=0, message="success")


@router.post("/sign-in")
async def sign_in(login_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, login_data.email)
    if not user:
        return APIResponse(retcode=400, message="Email not registered")

    if not await verify_password(db, login_data.email, login_data.password):
        return APIResponse(retcode=400, message="Invalid password")
    
    # 确保 user.id 转换为字符串
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # 建议添加 httponly 防止 XSS 攻击
        secure=False,   # 生产环境应设置为 True（需要 HTTPS）
        samesite="lax", # 建议添加 samesite 防止 CSRF 攻击
    )
    return APIResponse(retcode=0, message="success", data={"user_id": str(user.id)})

@router.get("/sign-out")
async def sign_out(response: Response):
    response.delete_cookie(key="access_token")
    return APIResponse(retcode=0, message="success")

@router.get("/")
async def auth(response: Response, user_id: str = Depends(get_current_user)):
    try:
        # 使用 get_current_user 验证 token
        print(user_id)
        
        # 如果返回的是字典（错误情况），说明 token 无效
        if isinstance(user_id, dict):
            response.delete_cookie(key="access_token")
            return APIResponse(**user_id)

        # Token 有效，返回成功
        return APIResponse(retcode=0, message="success", data=None)
    
    except Exception as e:
        # 处理其他异常
        response.delete_cookie(key="access_token")
        return APIResponse(retcode=401, message=str(e), data=None)
