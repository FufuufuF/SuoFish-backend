from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.curd.conversation import get_conversations_by_user_id
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.shcemas.api_response import APIResponse
from src.shcemas.chat import ConversationResponse

router = APIRouter()

@router.get("/")
def get_conversations(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = get_conversations_by_user_id(db, user_id)
    # 将 SQLAlchemy 模型转换为 Pydantic 模型
    conversations_data = [ConversationResponse.model_validate(conv) for conv in conversations]
    return APIResponse(retcode=0, message="success", data=conversations_data)