from pydantic import BaseModel, Field
from typing import Optional


class LikeBase(BaseModel):
    like_profile_id: int = Field(..., description="ID профиля, который лайкнули")
    contact: str = Field(..., max_length=20, description="Контактная информация")
    me_liked: bool = Field(..., description="Я лайкнул профиль")


class LikeCreate(LikeBase):
    role_id: int = Field(..., description="ID связанной роли")


class LikeUpdate(BaseModel):
    contact: Optional[str] = Field(None, max_length=20, description="Контактная информация")
    me_liked: Optional[bool] = Field(None, description="Я лайкнул профиль")


class LikeResponse(LikeBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True