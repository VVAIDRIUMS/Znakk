from fastapi import APIRouter
from app.api.profiles import router as profiles_router

router = APIRouter()
router.include_router(profiles_router)

# Можно добавить дополнительные маршруты или префиксы здесь