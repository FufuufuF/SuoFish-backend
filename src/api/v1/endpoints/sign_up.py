from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import bcrypt

from src.shcemas.api_response import APIResponse
from src.shcemas.sign import SignUp
from src.db.models.user import User
from src.curd.user import create_user
from src.curd.user import get_user_by_email
from src.api.deps import get_db

router = APIRouter()

@router.post("/")
async def sign_up(sign_up: SignUp, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_up.email)
    if user:
        return APIResponse(retcode=400, message="Email already registered")
    sign_up.password = bcrypt.hashpw(sign_up.password.encode('utf-8'), bcrypt.gensalt())
    user = Users(**sign_up.model_dump())
    create_user(db, user)
    return APIResponse(retcode=0, message="success")
