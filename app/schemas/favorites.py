from pydantic import BaseModel, Field
from typing import Optional


class FavoriteBase(BaseModel):
    favorite_profile_id: int = Field(..., description="ID профиля в избранном")
    contact: str = Field(..., max_length=20, description="Контактная информация")
    is_mutuai: bool = Field(..., description="Взаимность")


class FavoriteCreate(FavoriteBase):
    role_id: int = Field(..., description="ID связанной роли")


class FavoriteUpdate(BaseModel):
    contact: Optional[str] = Field(None, max_length=20, description="Контактная информация")
    is_mutuai: Optional[bool] = Field(None, description="Взаимность")


class FavoriteResponse(FavoriteBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True