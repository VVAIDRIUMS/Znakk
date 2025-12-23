from fastapi import APIRouter
from app.api.likes import router as likes_router

router = APIRouter()
router.include_router(likes_router)

# Можно добавить дополнительные маршруты или префиксы здесь