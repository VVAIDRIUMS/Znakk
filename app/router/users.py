# app/router/users.py
from fastapi import APIRouter
from app.api.users import router as users_api_router

router = APIRouter()
router.include_router(users_api_router)

# Можно добавить дополнительные префиксы или зависимости здесь
# Например:
# router = APIRouter(prefix="/users", tags=["users"])