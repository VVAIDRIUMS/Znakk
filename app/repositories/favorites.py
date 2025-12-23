from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.models.favorites import FavoriteModel
from app.schemas.favorites import FavoriteCreate, FavoriteUpdate


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, favorite_data: FavoriteCreate) -> FavoriteModel:
        favorite = FavoriteModel(**favorite_data.dict())
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        return favorite

    async def get_by_id(self, favorite_id: int) -> Optional[FavoriteModel]:
        result = await self.session.execute(
            select(FavoriteModel).where(FavoriteModel.id == favorite_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile_id(self, profile_id: int) -> Optional[FavoriteModel]:
        result = await self.session.execute(
            select(FavoriteModel).where(FavoriteModel.favorite_profile_id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FavoriteModel]:
        result = await self.session.execute(
            select(FavoriteModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, favorite_id: int, favorite_data: FavoriteUpdate) -> Optional[FavoriteModel]:
        stmt = (
            update(FavoriteModel)
            .where(FavoriteModel.id == favorite_id)
            .values(**favorite_data.dict(exclude_unset=True))
            .returning(FavoriteModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, favorite_id: int) -> bool:
        stmt = delete(FavoriteModel).where(FavoriteModel.id == favorite_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_role_id(self, role_id: int) -> List[FavoriteModel]:
        result = await self.session.execute(
            select(FavoriteModel).where(FavoriteModel.role_id == role_id)
        )
        return result.scalars().all()