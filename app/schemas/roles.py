from pydantic import BaseModel, Field
from typing import Optional, List


class RoleBase(BaseModel):
    name: str = Field(..., max_length=50, description="Название роли")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Название роли")


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


class RoleWithUsersResponse(RoleResponse):
    users: List[dict] = Field(default_factory=list, description="Пользователи с этой ролью")