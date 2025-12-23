from fastapi import APIRouter
from app.api.favorites import router as favorites_router

router = APIRouter()
router.include_router(favorites_router)

# Можно добавить дополнительные маршруты или префиксы здесь