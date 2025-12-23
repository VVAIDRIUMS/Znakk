from fastapi import APIRouter
from app.api.user_filters import router as user_filters_router

router = APIRouter()
router.include_router(user_filters_router)

# Можно добавить дополнительные маршруты или префиксы здесь