from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_filters import UserFilterRepository
from app.schemas.user_filters import (
    UserFilterCreate, 
    UserFilterUpdate, 
    UserFilterResponse,
    FilterStatsResponse,
    BulkFilterCreate
)
from app.exceptions import (
    UserFilterNotFoundException,
    UserFilterAlreadyExistsException,
    InvalidFilterDataException
)


class UserFilterService:
    def __init__(self, session: AsyncSession):
        self.repository = UserFilterRepository(session)

    async def create_filter(self, filter_data: UserFilterCreate) -> UserFilterResponse:
        # Проверяем, существует ли уже фильтр для этого пользователя
        existing = await self.repository.get_by_user_id(filter_data.user_id)
        if existing:
            raise UserFilterAlreadyExistsException(filter_data.user_id)
        
        filter_obj = await self.repository.create(filter_data)
        return UserFilterResponse.model_validate(filter_obj)

    async def create_filters_bulk(self, bulk_data: BulkFilterCreate) -> List[UserFilterResponse]:
        # Проверяем дубликаты по user_id
        user_ids = [f.user_id for f in bulk_data.filters]
        existing_filters = []
        for user_id in user_ids:
            existing = await self.repository.get_by_user_id(user_id)
            if existing:
                existing_filters.append(user_id)
        
        if existing_filters:
            raise UserFilterAlreadyExistsException(
                f"Filters already exist for users: {existing_filters}"
            )
        
        filters = await self.repository.create_bulk(bulk_data.filters)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def get_filter(self, filter_id: int) -> UserFilterResponse:
        filter_obj = await self.repository.get_by_id(filter_id)
        if not filter_obj:
            raise UserFilterNotFoundException(filter_id)
        return UserFilterResponse.model_validate(filter_obj)

    async def get_filter_by_user(self, user_id: int) -> UserFilterResponse:
        filter_obj = await self.repository.get_by_user_id(user_id)
        if not filter_obj:
            raise UserFilterNotFoundException(user_id, by_user_id=True)
        return UserFilterResponse.model_validate(filter_obj)

    async def get_all_filters(self, skip: int = 0, limit: int = 100) -> List[UserFilterResponse]:
        filters = await self.repository.get_all(skip, limit)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def update_filter(self, filter_id: int, filter_data: UserFilterUpdate) -> UserFilterResponse:
        # Проверяем существование фильтра
        existing_filter = await self.repository.get_by_id(filter_id)
        if not existing_filter:
            raise UserFilterNotFoundException(filter_id)
        
        # Если обновляется user_id, проверяем его уникальность
        if filter_data.user_id is not None:
            filter_with_user_id = await self.repository.get_by_user_id(filter_data.user_id)
            if filter_with_user_id and filter_with_user_id.id != filter_id:
                raise UserFilterAlreadyExistsException(filter_data.user_id)
        
        filter_obj = await self.repository.update(filter_id, filter_data)
        if not filter_obj:
            raise UserFilterNotFoundException(filter_id)
        return UserFilterResponse.model_validate(filter_obj)

    async def delete_filter(self, filter_id: int) -> Dict[str, Any]:
        success = await self.repository.delete(filter_id)
        if not success:
            raise UserFilterNotFoundException(filter_id)
        return {"message": "Filter deleted successfully"}

    async def delete_filter_by_user(self, user_id: int) -> Dict[str, Any]:
        success = await self.repository.delete_by_user_id(user_id)
        if not success:
            raise UserFilterNotFoundException(user_id, by_user_id=True)
        return {"message": f"Filter for user {user_id} deleted successfully"}

    async def get_filters_by_role(self, role_id: int) -> List[UserFilterResponse]:
        filters = await self.repository.get_by_role_id(role_id)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def search_filters(
        self,
        gender_filter: Optional[str] = None,
        city_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserFilterResponse]:
        filters = await self.repository.search_filters(
            gender_filter=gender_filter,
            city_filter=city_filter,
            skip=skip,
            limit=limit
        )
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def get_filters_by_gender(self, gender: str) -> List[UserFilterResponse]:
        filters = await self.repository.get_filters_by_gender(gender)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def get_filters_by_city(self, city: str) -> List[UserFilterResponse]:
        filters = await self.repository.get_filters_by_city(city)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def get_filter_stats(self) -> FilterStatsResponse:
        stats = await self.repository.get_stats()
        return FilterStatsResponse(**stats)

    async def get_users_by_filter_criteria(self, gender: str, city: str) -> List[UserFilterResponse]:
        filters = await self.repository.get_users_by_filters(gender, city)
        return [UserFilterResponse.model_validate(f) for f in filters]

    async def apply_filters_to_profiles(
        self, 
        profiles: List[Dict[str, Any]], 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Применяет фильтры пользователя к списку профилей"""
        filter_obj = await self.repository.get_by_user_id(user_id)
        if not filter_obj:
            return profiles  # Если фильтра нет, возвращаем все профили
        
        filtered_profiles = []
        for profile in profiles:
            # Применяем гендерный фильтр
            if filter_obj.gender_filter not in ['any', 'all', 'любой']:
                if profile.get('gender') != filter_obj.gender_filter:
                    continue
            
            # Применяем фильтр по городу
            if filter_obj.city_filter:
                if filter_obj.city_filter not in profile.get('city', ''):
                    continue
            
            filtered_profiles.append(profile)
        
        return filtered_profiles