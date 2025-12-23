from pydantic import BaseModel
from typing import Optional


class UserRoleRelationBase(BaseModel):
    """Базовая схема связи пользователя и роли"""
    user_id: int
    role_id: int


class UserRoleRelationCreate(UserRoleRelationBase):
    """Схема для создания связи пользователя и роли"""
    pass


class UserRoleRelationUpdate(BaseModel):
    """Схема для обновления связи пользователя и роли"""
    role_id: Optional[int] = None


class UserRoleRelationResponse(UserRoleRelationBase):
    """Схема ответа связи пользователя и роли"""
    id: int
    
    class Config:
        from_attributes = True


# Если нужен импорт SUserGet, используем алиас
try:
    from app.schemas.users import SUserGet
except ImportError:
    # Создаем простую схему если импорт не удался
    class SUserGet(BaseModel):
        id: int
        email: str
        is_active: bool = True
        role_id: int