from fastapi import APIRouter
from src.api.v1.endpoints.sign_up import router as sign_up_router
from src.api.v1.endpoints.sign_in import router as sign_in_router
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.conversations import router as conversations_router
from src.api.v1.endpoints.get_messages import router as get_messages_router

router = APIRouter()

router.include_router(sign_up_router, prefix="/sign-up")
router.include_router(sign_in_router, prefix="/sign-in")
router.include_router(auth_router, prefix="/auth")
router.include_router(chat_router, prefix="/chat")
router.include_router(conversations_router, prefix="/conversations")
router.include_router(get_messages_router, prefix="/messages")