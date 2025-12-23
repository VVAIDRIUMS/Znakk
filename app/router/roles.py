from fastapi import APIRouter
from app.api.roles import router as roles_router

router = APIRouter()
router.include_router(roles_router)

# Можно добавить дополнительные маршруты или префиксы здесь