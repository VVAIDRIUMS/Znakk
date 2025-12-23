from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.models.roles import RoleModel
from app.schemas.roles import RoleCreate, RoleUpdate


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role_data: RoleCreate) -> RoleModel:
        role = RoleModel(**role_data.dict())
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def get_by_id(self, role_id: int) -> Optional[RoleModel]:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        result = await self.session.execute(
            select(RoleModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, role_id: int, role_data: RoleUpdate) -> Optional[RoleModel]:
        stmt = (
            update(RoleModel)
            .where(RoleModel.id == role_id)
            .values(**role_data.dict(exclude_unset=True))
            .returning(RoleModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, role_id: int) -> bool:
        # Проверяем, есть ли пользователи с этой ролью
        role = await self.get_by_id(role_id)
        if role and role.users:
            return False  # Нельзя удалить роль, если есть пользователи
        
        stmt = delete(RoleModel).where(RoleModel.id == role_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        result = await self.session.execute(
            select(RoleModel)
            .where(RoleModel.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()