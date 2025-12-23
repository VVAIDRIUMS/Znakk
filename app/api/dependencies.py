from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, Field

from app.database.database import async_session_maker
from app.exceptions.auth import (
    InvalidJWTTokenError,
    InvalidTokenHTTPError,
    NoAccessTokenHTTPError,
)
from app.services.auth import AuthService
from app.database.db_manager import DBManager
from app.schemas.users import UserResponse


class PaginationParams(BaseModel):
    page: int | None = Field(default=1, ge=1)
    per_page: int | None = Field(default=5, ge=1, le=30)


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if token is None:
        raise NoAccessTokenHTTPError
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    try:
        data = AuthService.decode_token(token)
    except InvalidJWTTokenError:
        raise InvalidTokenHTTPError
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


# ✅ НОВОЕ: Получить текущего пользователя
# Возвращает UserResponse с информацией о пользователе из токена
async def get_current_user(
    user_id: int = Depends(get_current_user_id)
) -> UserResponse:
    """
    Получить информацию о текущем пользователе
    Требует: valid JWT token
    Возвращает: UserResponse с информацией из токена
    
    Примечание: Эта функция возвращает только то что есть в токене
    Для получения данных из БД используйте отдельный запрос
    """
    # Простой способ - создаем UserResponse с только ID
    # Это подходит для проверок в likes.py
    return UserResponse(id=user_id, email="", is_active=True, role_id=1)
