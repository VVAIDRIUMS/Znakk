from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    is_active: bool = Field(default=True, description="Активен ли пользователь")


# Схема для добавления пользователя
class SUserAdd(UserBase):
    """Схема для добавления пользователя"""
    password: str = Field(..., min_length=8, max_length=100, description="Пароль")
    role_id: int = Field(..., ge=1, description="ID роли пользователя")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        if not any(char.isdigit() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(char.isalpha() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v


# Схема для получения пользователя (отсутствовала!)
class SUserGet(UserBase):
    """Схема для получения пользователя"""
    id: int = Field(..., description="ID пользователя")
    role_id: int = Field(..., description="ID роли пользователя")
    created_at: Optional[datetime] = Field(None, description="Дата создания")
    
    class Config:
        from_attributes = True


# Схема для создания пользователя
class UserCreate(SUserAdd):
    """Схема для создания пользователя"""
    pass


# Схема для обновления пользователя
class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="Новый пароль")
    is_active: Optional[bool] = Field(None, description="Активен ли пользователь")
    role_id: Optional[int] = Field(None, ge=1, description="ID роли пользователя")


# Схема для входа пользователя
class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль")


# Схема ответа пользователя
class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: int
    role_id: int
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")

    class Config:
        from_attributes = True


# Схема ответа с пользователем и ролью
class UserWithRoleResponse(UserResponse):
    """Схема для ответа с данными пользователя и ролью"""
    role_name: str = Field(..., description="Название роли")


# Токен
class Token(BaseModel):
    """Схема для токена"""
    access_token: str = Field(..., description="Access токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    user_id: int = Field(..., description="ID пользователя")
    role_id: int = Field(..., description="ID роли пользователя")


# Данные токена
class TokenData(BaseModel):
    """Схема для данных токена"""
    user_id: Optional[int] = None
    email: Optional[str] = None


# Смена пароля
class PasswordChange(BaseModel):
    """Схема для смены пароля"""
    current_password: str = Field(..., min_length=8, max_length=100, description="Текущий пароль")
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль")

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        if not any(char.isdigit() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(char.isalpha() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v


# Статистика пользователей
class UserStatsResponse(BaseModel):
    """Схема для статистики пользователей"""
    total_users: int = Field(..., description="Всего пользователей")
    active_users: int = Field(..., description="Активных пользователей")
    inactive_users: int = Field(..., description="Неактивных пользователей")
    users_by_role: dict = Field(..., description="Пользователи по ролям")


# Алиасы для обратной совместимости
SUserGet = UserResponse  # Алиас для SUserGet