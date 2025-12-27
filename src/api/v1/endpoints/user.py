from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db

from src.utils.authentic import get_current_user
from src.schemas.api_response import APIResponse
from src.crud.user import get_user_by_id
from src.schemas.user import UserResponse

router = APIRouter()

@router.get("/")
async def get_user(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        return APIResponse(retcode=404, message="User not found")
    response = UserResponse.model_validate(user)
    return APIResponse(retcode=0, message="success", data=response)

