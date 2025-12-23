from pydantic import BaseModel, Field
from typing import Optional


class LikeCreate(BaseModel):
    """Создание лайка"""
    liked_profile_id: int = Field(..., description="ID профиля, который лайкнули")

    class Config:
        from_attributes = True


class LikeResponse(BaseModel):
    """Ответ с информацией о лайке"""
    id: int
    user_id: int
    liked_profile_id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
