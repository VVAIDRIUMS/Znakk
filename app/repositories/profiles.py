from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_, or_
from app.models.profiles import ProfileModel
from app.schemas.profiles import ProfileCreate, ProfileUpdate


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile_data: ProfileCreate) -> ProfileModel:
        profile = ProfileModel(**profile_data.dict())
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_by_id(self, profile_id: int) -> Optional[ProfileModel]:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[ProfileModel]:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProfileModel]:
        result = await self.session.execute(
            select(ProfileModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, profile_id: int, profile_data: ProfileUpdate) -> Optional[ProfileModel]:
        stmt = (
            update(ProfileModel)
            .where(ProfileModel.id == profile_id)
            .values(**profile_data.dict(exclude_unset=True))
            .returning(ProfileModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, profile_id: int) -> bool:
        stmt = delete(ProfileModel).where(ProfileModel.id == profile_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_role_id(self, role_id: int) -> List[ProfileModel]:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.role_id == role_id)
        )
        return result.scalars().all()

    async def search_profiles(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        gender: Optional[str] = None,
        city: Optional[str] = None,
        tags: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProfileModel]:
        query = select(ProfileModel)
        
        if min_age is not None:
            query = query.where(ProfileModel.age >= min_age)
        if max_age is not None:
            query = query.where(ProfileModel.age <= max_age)
        if gender:
            query = query.where(ProfileModel.gender == gender)
        if city:
            query = query.where(ProfileModel.city.ilike(f"%{city}%"))
        if tags:
            query = query.where(ProfileModel.tags.ilike(f"%{tags}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_username(self, username: str) -> Optional[ProfileModel]:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.username == username)
        )
        return result.scalar_one_or_none()