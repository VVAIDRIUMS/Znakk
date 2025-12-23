from pydantic import BaseModel, Field, validator
from typing import Optional, List


class UserFilterBase(BaseModel):
    user_id: int = Field(..., description="ID пользователя", ge=1)
    gender_filter: str = Field(..., max_length=20, description="Фильтр по полу")
    city_filter: str = Field(..., max_length=30, description="Фильтр по городу")

    @validator('gender_filter')
    def validate_gender_filter(cls, v):
        valid_genders = ['male', 'female', 'any', 'all', 'мужской', 'женский', 'любой']
        if v.lower() not in valid_genders:
            raise ValueError(f"gender_filter must be one of: {', '.join(valid_genders)}")
        return v.lower()


class UserFilterCreate(UserFilterBase):
    role_id: int = Field(..., description="ID связанной роли", ge=1)


class UserFilterUpdate(BaseModel):
    gender_filter: Optional[str] = Field(None, max_length=20, description="Фильтр по полу")
    city_filter: Optional[str] = Field(None, max_length=30, description="Фильтр по городу")
    role_id: Optional[int] = Field(None, ge=1, description="ID связанной роли")


class UserFilterResponse(UserFilterBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True


class FilterStatsResponse(BaseModel):
    total_filters: int = Field(..., description="Общее количество фильтров")
    gender_stats: dict = Field(..., description="Статистика по гендерным фильтрам")
    city_stats: dict = Field(..., description="Статистика по городским фильтрам")


class BulkFilterCreate(BaseModel):
    filters: List[UserFilterCreate] = Field(..., description="Список фильтров для создания")