from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.roles import RoleRepository
from app.schemas.roles import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsersResponse
from app.exceptions import (
    RoleNotFoundException, 
    RoleAlreadyExistsException,
    RoleHasUsersException
)


class RoleService:
    def __init__(self, session: AsyncSession):
        self.repository = RoleRepository(session)

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        # Проверяем, существует ли уже роль с таким именем
        existing = await self.repository.get_by_name(role_data.name)
        if existing:
            raise RoleAlreadyExistsException(role_data.name)
        
        role = await self.repository.create(role_data)
        return RoleResponse.model_validate(role)

    async def get_role(self, role_id: int, include_users: bool = False) -> RoleResponse | RoleWithUsersResponse:
        role = await self.repository.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException(role_id)
        
        if include_users:
            users_data = [{"id": user.id, "username": user.username} for user in role.users]
            return RoleWithUsersResponse(
                id=role.id,
                name=role.name,
                users=users_data
            )
        
        return RoleResponse.model_validate(role)

    async def get_role_by_name(self, name: str) -> RoleResponse:
        role = await self.repository.get_by_name(name)
        if not role:
            raise RoleNotFoundException(name, by_name=True)
        return RoleResponse.model_validate(role)

    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[RoleResponse]:
        roles = await self.repository.get_all(skip, limit)
        return [RoleResponse.model_validate(role) for role in roles]

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleResponse:
        # Проверяем существование роли
        existing_role = await self.repository.get_by_id(role_id)
        if not existing_role:
            raise RoleNotFoundException(role_id)
        
        # Если обновляется имя, проверяем его уникальность
        if role_data.name is not None:
            role_with_name = await self.repository.get_by_name(role_data.name)
            if role_with_name and role_with_name.id != role_id:
                raise RoleAlreadyExistsException(role_data.name)
        
        role = await self.repository.update(role_id, role_data)
        if not role:
            raise RoleNotFoundException(role_id)
        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: int) -> Dict[str, Any]:
        success = await self.repository.delete(role_id)
        if not success:
            # Проверяем, почему не удалось удалить
            role = await self.repository.get_by_id(role_id)
            if not role:
                raise RoleNotFoundException(role_id)
            elif role.users:
                raise RoleHasUsersException(role_id, len(role.users))
            else:
                raise RoleNotFoundException(role_id)
        
        return {"message": "Role deleted successfully"}

    async def search_roles(self, name: str, skip: int = 0, limit: int = 100) -> List[RoleResponse]:
        roles = await self.repository.search_by_name(name, skip, limit)
        return [RoleResponse.model_validate(role) for role in roles]

    async def get_role_with_users(self, role_id: int) -> RoleWithUsersResponse:
        role = await self.repository.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException(role_id)
        
        users_data = [{"id": user.id, "username": user.username} for user in role.users]
        return RoleWithUsersResponse(
            id=role.id,
            name=role.name,
            users=users_data
        )