from fastapi import APIRouter, Depends
import bcrypt

from src.shcemas.api_response import APIResponse
from src.shcemas.sign import SignIn
from src.curd.user import get_user_by_email
from src.api.deps import get_db
from sqlalchemy.orm import Session
from src.curd.user import get_user_hash_password

router = APIRouter()

def verify_password(email: str, login_password: str):
    hashed_password = get_user_hash_password(email)
    return bcrypt.checkpw(login_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/")
async def sign_in(sign_in: SignIn, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_in.email)
    if not user:
        return APIResponse(retcode=400, message="Email not registered")

    if not verify_password(sign_in.email, sign_in.password):
        return APIResponse(retcode=400, message="Invalid password")
    
    return APIResponse(retcode=0, message="success")