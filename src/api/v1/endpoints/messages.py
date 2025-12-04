from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.conversation import get_conversation_by_id
from src.schemas.chat import MessageResponse
from src.crud.message import get_messages_by_conversation_id
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.schemas.api_response import APIResponse

router = APIRouter()


@router.get("/{conversation_id}")
async def get_messages(
    conversation_id: int,  # 路径参数
    user_id: int = Depends(get_current_user),  # 认证
    db: AsyncSession = Depends(get_db)
):
    if not conversation_id:
        return APIResponse(retcode=400, message="Conversation ID is required")
    
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        return APIResponse(retcode=400, message="Conversation not found")
    
    if conversation.user_id != user_id:
        return APIResponse(retcode=400, message="Unauthorized access to conversation")
    messages = await get_messages_by_conversation_id(db, conversation_id)
    messages_data = [MessageResponse.model_validate(message) for message in messages]
    return APIResponse(retcode=0, message="success", data=messages_data)
