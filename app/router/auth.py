from fastapi import APIRouter
from app.api.auth import router as auth_api_router

router = APIRouter()
router.include_router(auth_api_router)