from fastapi import APIRouter
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.conversations import router as conversations_router
from src.api.v1.endpoints.messages import router as messages_router
from src.api.v1.endpoints.model import router as model_router
from src.api.v1.endpoints.knowledge_base import router as knowledge_base_router
from src.api.v1.endpoints.conversation_log import router as conversation_log_router
from src.api.v1.endpoints.user import router as user_router
router = APIRouter()

# 保持原有 API 接口不变
router.include_router(auth_router, prefix="/auth")
router.include_router(chat_router, prefix="/chat")
router.include_router(conversations_router, prefix="/conversations")
router.include_router(messages_router, prefix="/messages")
router.include_router(model_router, prefix="/model")
router.include_router(knowledge_base_router, prefix="/knowledge-base")
router.include_router(conversation_log_router, prefix="/conversation-logs")
router.include_router(user_router, prefix="/user")