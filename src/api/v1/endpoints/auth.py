from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import bcrypt

from src.schemas.api_response import APIResponse
from src.schemas.sign import SignUp, SignIn
from src.db.models.user import User
from src.crud.user import create_user, get_user_by_email, get_user_hash_password
from src.api.deps import get_db
from src.utils.authentic import create_access_token, get_current_user

router = APIRouter()

# 用于挂载到不同前缀的子路由
sign_up_router = APIRouter()
sign_in_router = APIRouter()
verify_router = APIRouter()


def verify_password(db: Session, email: str, login_password: str):
    hashed_password = get_user_hash_password(db, email)
    return bcrypt.checkpw(login_password.encode('utf-8'), hashed_password.encode('utf-8'))


@sign_up_router.post("/")
async def sign_up(sign_up: SignUp, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_up.email)
    if user:
        return APIResponse(retcode=400, message="Email already registered")
    sign_up.password = bcrypt.hashpw(sign_up.password.encode('utf-8'), bcrypt.gensalt())
    user = User(**sign_up.model_dump())
    create_user(db, user)
    return APIResponse(retcode=0, message="success")


@sign_in_router.post("/")
async def sign_in(sign_in: SignIn, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_in.email)
    if not user:
        return APIResponse(retcode=400, message="Email not registered")

    if not verify_password(db, sign_in.email, sign_in.password):
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


@verify_router.get("/")
def verify(user_id: str = Depends(get_current_user)):
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
