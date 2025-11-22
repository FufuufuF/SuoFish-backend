from fastapi import APIRouter
from src.api.v1.endpoints.sign_up import router as sign_up_router
from src.api.v1.endpoints.sign_in import router as sign_in_router

router = APIRouter()

router.include_router(sign_up_router, prefix="/sign-up")
router.include_router(sign_in_router, prefix="/sign-in")