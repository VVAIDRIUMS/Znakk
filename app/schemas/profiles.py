from pydantic import BaseModel, Field
from typing import Optional


class ProfileBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя", ge=1)
    username: str = Field(..., max_length=50, description="Имя пользователя")
    age: int = Field(..., description="Возраст", ge=18, le=120)
    gender: str = Field(..., max_length=20, description="Пол")
    city: str = Field(..., max_length=30, description="Город")
    description: str = Field(..., max_length=100, description="Описание профиля")
    tags: str = Field(..., max_length=100, description="Теги профиля")
    photo: str = Field(..., max_length=200, description="URL фотографии")


class ProfileCreate(ProfileBase):
    role_id: int = Field(..., description="ID связанной роли", ge=1)


class ProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50, description="Имя пользователя")
    age: Optional[int] = Field(None, ge=18, le=120, description="Возраст")
    gender: Optional[str] = Field(None, max_length=20, description="Пол")
    city: Optional[str] = Field(None, max_length=30, description="Город")
    description: Optional[str] = Field(None, max_length=100, description="Описание профиля")
    tags: Optional[str] = Field(None, max_length=100, description="Теги профиля")
    photo: Optional[str] = Field(None, max_length=200, description="URL фотографии")
    role_id: Optional[int] = Field(None, ge=1, description="ID связанной роли")


class ProfileResponse(ProfileBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True