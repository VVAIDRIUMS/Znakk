from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_
from app.models.likes import LikeModel
from app.schemas.likes import LikeCreate, LikeUpdate


class LikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, like_data: LikeCreate) -> LikeModel:
        like = LikeModel(**like_data.dict())
        self.session.add(like)
        await self.session.commit()
        await self.session.refresh(like)
        return like

    # ✅ НОВОЕ: Получить лайк по user_id
    async def get_by_user_id(self, user_id: int) -> List[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.user_id == user_id)
        )
        return result.scalars().all()

    # ✅ НОВОЕ: Получить лайк по liked_profile_id
    async def get_by_liked_profile_id(self, liked_profile_id: int) -> List[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.liked_profile_id == liked_profile_id)
        )
        return result.scalars().all()

    # ✅ НОВОЕ: Получить лайк по user_id и liked_profile_id
    async def get_by_user_and_profile(self, user_id: int, liked_profile_id: int) -> Optional[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(
                and_(
                    LikeModel.user_id == user_id,
                    LikeModel.liked_profile_id == liked_profile_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, like_id: int) -> Optional[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.id == like_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile_id(self, profile_id: int) -> Optional[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.liked_profile_id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, like_id: int, like_data: LikeUpdate) -> Optional[LikeModel]:
        stmt = (
            update(LikeModel)
            .where(LikeModel.id == like_id)
            .values(**like_data.dict(exclude_unset=True))
            .returning(LikeModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, like_id: int) -> bool:
        stmt = delete(LikeModel).where(LikeModel.id == like_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_role_id(self, role_id: int) -> List[LikeModel]:
        result = await self.session.execute(
            select(LikeModel).where(LikeModel.role_id == role_id)
        )
        return result.scalars().all()

    async def get_mutual_likes(self) -> List[LikeModel]:
        # Получаем все лайки
        result = await self.session.execute(select(LikeModel))
        return result.scalars().all()
