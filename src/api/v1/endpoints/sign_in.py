from fastapi import APIRouter, Depends, Response
import bcrypt

from src.shcemas.api_response import APIResponse
from src.shcemas.sign import SignIn
from src.curd.user import get_user_by_email
from src.api.deps import get_db
from sqlalchemy.orm import Session
from src.curd.user import get_user_hash_password
from src.utils.authentic import create_access_token

router = APIRouter()

def verify_password(db: Session, email: str, login_password: str):
    hashed_password = get_user_hash_password(db, email)
    return bcrypt.checkpw(login_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/")
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
    return APIResponse(retcode=0, message="success", data={"user_id": str(user.user_id)})