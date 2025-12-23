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


# ✅ ИСПРАВЛЕНО: Получить токен из заголовка Authorization
def get_token(request: Request) -> str:
    """
    Получить JWT токен из заголовка Authorization
    Формат: Authorization: Bearer <token>
    """
    # 1️⃣ Сначала пробуем получить из cookies (для обратной совместимости)
    token = request.cookies.get("access_token", None)
    if token:
        return token
    
    # 2️⃣ Если нет в cookies, ищем в заголовке Authorization
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header:
        print("❌ ОШИБКА: Нет заголовка Authorization")
        print(f"📋 Доступные заголовки: {dict(request.headers)}")
        raise NoAccessTokenHTTPError
    
    # 3️⃣ Проверяем что формат правильный: "Bearer <token>"
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        print(f"❌ ОШИБКА: Неверный формат заголовка: {auth_header}")
        print("✅ Правильный формат: Authorization: Bearer <token>")
        raise NoAccessTokenHTTPError
    
    token = parts[1]
    
    if not token:
        print("❌ ОШИБКА: Токен пуст")
        raise NoAccessTokenHTTPError
    
    print(f"✅ Получен токен из Authorization: {token[:20]}...")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """
    Получить ID пользователя из токена
    Декодирует JWT и извлекает user_id
    """
    try:
        data = AuthService.decode_token(token)
        print(f"✅ Токен успешно декодирован: user_id = {data.get('user_id')}")
    except InvalidJWTTokenError as e:
        print(f"❌ ОШИБКА при декодировании токена: {e}")
        raise InvalidTokenHTTPError
    
    user_id = data.get("user_id")
    if not user_id:
        print("❌ ОШИБКА: user_id не найден в токене")
        print(f"📋 Содержимое токена: {data}")
        raise InvalidTokenHTTPError
    
    return user_id


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
