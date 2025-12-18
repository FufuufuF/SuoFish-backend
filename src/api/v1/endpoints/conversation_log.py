from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.conversation_log import get_log_session_by_conversation, get_log_rounds_by_session
from src.schemas.conversation_log import ConversationLogResponse, ConversationLogRequest
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.schemas.api_response import APIResponse

router = APIRouter()

@router.post("/get-logs")
async def get_log(
    request: ConversationLogRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    log_session = await get_log_session_by_conversation(db, request.conversation_id)
    if not log_session:
        return APIResponse(retcode=400, message="Log session not found")
    log_rounds = await get_log_rounds_by_session(db, log_session.id)
    response = [ConversationLogResponse.model_validate(log_round) for log_round in log_rounds]
    return APIResponse(retcode=0, message="success", data={ "conversation_logs": response })