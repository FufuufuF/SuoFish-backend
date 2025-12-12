from fastapi import APIRouter
from src.api.v1.endpoints.auth import sign_up_router, sign_in_router, verify_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.conversations import router as conversations_router
from src.api.v1.endpoints.messages import router as messages_router
from src.api.v1.endpoints.model import router as model_router

router = APIRouter()

# 保持原有 API 接口不变
router.include_router(sign_up_router, prefix="/sign-up")
router.include_router(sign_in_router, prefix="/sign-in")
router.include_router(verify_router, prefix="/auth")
router.include_router(chat_router, prefix="/chat")
router.include_router(conversations_router, prefix="/conversations")
router.include_router(messages_router, prefix="/messages")
router.include_router(model_router, prefix="/model")
