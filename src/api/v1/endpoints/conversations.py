from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.conversation import get_conversation_by_id, get_conversations_by_user_id, delete_conversation_by_id
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.schemas.api_response import APIResponse
from src.schemas.chat import ConversationResponse

router = APIRouter()


@router.get("/")
async def get_conversations(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    conversations = await get_conversations_by_user_id(db, user_id)
    # 将 SQLAlchemy 模型转换为 Pydantic 模型
    conversations_data = [ConversationResponse.model_validate(conv) for conv in conversations]
    return APIResponse(retcode=0, message="success", data=conversations_data)


@router.get("/delete/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        return APIResponse(retcode=400, message="Conversation not found")
    if conversation.user_id != user_id:
        return APIResponse(retcode=400, message="Unauthorized access to conversation")
    delete_result = await delete_conversation_by_id(db, conversation_id)
    if delete_result:
        return APIResponse(retcode=0, message="success")
    else:
        return APIResponse(retcode=400, message="Failed to delete conversation")
