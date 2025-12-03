from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.schemas.chat import Chat
from src.services.chat_service import ChatService
from src.utils.authentic import get_current_user
from src.api.deps import get_db

router = APIRouter()


@router.post("/")
async def chat(
    chat: Chat,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    聊天接口 - 流式返回 LLM 响应
    
    返回 NDJSON 格式的流式响应:
    - {"token": "..."} - LLM 生成的 token
    - {"error": "..."} - 错误信息  
    - {"metadata": {...}} - 完成后的元数据
    """
    chat_service = ChatService(db)
    return StreamingResponse(
        chat_service.process_chat(
            user_message=chat.user_message,
            user_id=user_id,
            conversation_id=chat.conversation_id
        ),
        media_type="application/x-ndjson"
    )
