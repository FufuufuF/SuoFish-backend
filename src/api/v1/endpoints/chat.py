from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.shcemas.llm_config import MessageMetadata
from src.shcemas.api_response import APIResponse
from src.llm.llm_service import LLMService
from src.shcemas.chat import Chat
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
async def chat(
    chat: Chat,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    async def generate():
        llm_service = LLMService()
        async for token in llm_service.generate_chat_response(chat.user_message):
            yield f'{{"token": "{token}"}}\n'
        
        metadata_json = MessageMetadata(
            llm_message_id='0',
            user_message_id='0',
        )
        yield f'{{"metadata": {metadata_json.json()}}}\n'
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")