from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.shcemas.chat import MessageResponse
from src.curd.message import get_messages_by_conversation_id
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.shcemas.api_response import APIResponse

router = APIRouter()

@router.get("/{conversation_id}")
def get_messages(
    conversation_id: int,  # 路径参数
    user_id: int = Depends(get_current_user),  # 认证
    db: Session = Depends(get_db)
):
    messages = get_messages_by_conversation_id(db, conversation_id)
    messages_data = [MessageResponse.model_validate(message) for message in messages]
    return APIResponse(retcode=0, message="success", data=messages_data)