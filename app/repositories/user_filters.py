from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_
from app.models.user_filters import User_filterModel
from app.schemas.user_filters import UserFilterCreate, UserFilterUpdate


class UserFilterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, filter_data: UserFilterCreate) -> User_filterModel:
        filter_obj = User_filterModel(**filter_data.dict())
        self.session.add(filter_obj)
        await self.session.commit()
        await self.session.refresh(filter_obj)
        return filter_obj

    async def create_bulk(self, filters_data: List[UserFilterCreate]) -> List[User_filterModel]:
        filters = [User_filterModel(**data.dict()) for data in filters_data]
        self.session.add_all(filters)
        await self.session.commit()
        for filter_obj in filters:
            await self.session.refresh(filter_obj)
        return filters

    async def get_by_id(self, filter_id: int) -> Optional[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(User_filterModel.id == filter_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(User_filterModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, filter_id: int, filter_data: UserFilterUpdate) -> Optional[User_filterModel]:
        stmt = (
            update(User_filterModel)
            .where(User_filterModel.id == filter_id)
            .values(**filter_data.dict(exclude_unset=True))
            .returning(User_filterModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, filter_id: int) -> bool:
        stmt = delete(User_filterModel).where(User_filterModel.id == filter_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_by_user_id(self, user_id: int) -> bool:
        stmt = delete(User_filterModel).where(User_filterModel.user_id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_role_id(self, role_id: int) -> List[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(User_filterModel.role_id == role_id)
        )
        return result.scalars().all()

    async def search_filters(
        self,
        gender_filter: Optional[str] = None,
        city_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User_filterModel]:
        query = select(User_filterModel)
        
        if gender_filter:
            query = query.where(User_filterModel.gender_filter.ilike(f"%{gender_filter}%"))
        if city_filter:
            query = query.where(User_filterModel.city_filter.ilike(f"%{city_filter}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_filters_by_gender(self, gender: str) -> List[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(User_filterModel.gender_filter == gender)
        )
        return result.scalars().all()

    async def get_filters_by_city(self, city: str) -> List[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(User_filterModel.city_filter.ilike(f"%{city}%"))
        )
        return result.scalars().all()

    async def get_stats(self) -> Dict[str, Any]:
        # Общее количество фильтров
        total_result = await self.session.execute(
            select(func.count()).select_from(User_filterModel)
        )
        total_filters = total_result.scalar()

        # Статистика по гендерным фильтрам
        gender_result = await self.session.execute(
            select(
                User_filterModel.gender_filter,
                func.count(User_filterModel.id)
            )
            .group_by(User_filterModel.gender_filter)
        )
        gender_stats = {row[0]: row[1] for row in gender_result.all()}

        # Статистика по городам (топ 10)
        city_result = await self.session.execute(
            select(
                User_filterModel.city_filter,
                func.count(User_filterModel.id)
            )
            .group_by(User_filterModel.city_filter)
            .order_by(func.count(User_filterModel.id).desc())
            .limit(10)
        )
        city_stats = {row[0]: row[1] for row in city_result.all()}

        return {
            "total_filters": total_filters,
            "gender_stats": gender_stats,
            "city_stats": city_stats
        }

    async def get_users_by_filters(self, gender: str, city: str) -> List[User_filterModel]:
        result = await self.session.execute(
            select(User_filterModel).where(
                and_(
                    User_filterModel.gender_filter == gender,
                    User_filterModel.city_filter.ilike(f"%{city}%")
                )
            )
        )
        return result.scalars().all()