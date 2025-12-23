from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.profiles import ProfileRepository
from app.schemas.profiles import ProfileCreate, ProfileUpdate, ProfileResponse
from app.exceptions import (
    ProfileNotFoundException, 
    ProfileAlreadyExistsException,
    InvalidProfileDataException
)


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.repository = ProfileRepository(session)

    async def create_profile(self, profile_data: ProfileCreate) -> ProfileResponse:
        # Проверяем, существует ли уже профиль с таким user_id
        existing_by_user_id = await self.repository.get_by_user_id(profile_data.user_id)
        if existing_by_user_id:
            raise ProfileAlreadyExistsException(f"Profile with user_id {profile_data.user_id} already exists")
        
        # Проверяем, существует ли уже профиль с таким username
        existing_by_username = await self.repository.get_by_username(profile_data.username)
        if existing_by_username:
            raise ProfileAlreadyExistsException(f"Profile with username {profile_data.username} already exists")
        
        profile = await self.repository.create(profile_data)
        return ProfileResponse.model_validate(profile)

    async def get_profile(self, profile_id: int) -> ProfileResponse:
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ProfileNotFoundException(profile_id)
        return ProfileResponse.model_validate(profile)

    async def get_profile_by_user_id(self, user_id: int) -> ProfileResponse:
        profile = await self.repository.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundException(user_id, by_user_id=True)
        return ProfileResponse.model_validate(profile)

    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> List[ProfileResponse]:
        profiles = await self.repository.get_all(skip, limit)
        return [ProfileResponse.model_validate(profile) for profile in profiles]

    async def update_profile(self, profile_id: int, profile_data: ProfileUpdate) -> ProfileResponse:
        # Проверяем существование профиля
        existing_profile = await self.repository.get_by_id(profile_id)
        if not existing_profile:
            raise ProfileNotFoundException(profile_id)
        
        # Если обновляется username, проверяем его уникальность
        if profile_data.username is not None:
            profile_with_username = await self.repository.get_by_username(profile_data.username)
            if profile_with_username and profile_with_username.id != profile_id:
                raise ProfileAlreadyExistsException(f"Profile with username {profile_data.username} already exists")
        
        # Если обновляется user_id, проверяем его уникальность
        if profile_data.user_id is not None:
            profile_with_user_id = await self.repository.get_by_user_id(profile_data.user_id)
            if profile_with_user_id and profile_with_user_id.id != profile_id:
                raise ProfileAlreadyExistsException(f"Profile with user_id {profile_data.user_id} already exists")
        
        profile = await self.repository.update(profile_id, profile_data)
        if not profile:
            raise ProfileNotFoundException(profile_id)
        return ProfileResponse.model_validate(profile)

    async def delete_profile(self, profile_id: int) -> Dict[str, Any]:
        success = await self.repository.delete(profile_id)
        if not success:
            raise ProfileNotFoundException(profile_id)
        return {"message": "Profile deleted successfully"}

    async def get_profiles_by_role(self, role_id: int) -> List[ProfileResponse]:
        profiles = await self.repository.get_by_role_id(role_id)
        return [ProfileResponse.model_validate(profile) for profile in profiles]

    async def search_profiles(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        gender: Optional[str] = None,
        city: Optional[str] = None,
        tags: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProfileResponse]:
        # Валидация параметров поиска
        if min_age is not None and max_age is not None and min_age > max_age:
            raise InvalidProfileDataException("min_age cannot be greater than max_age")
        
        profiles = await self.repository.search_profiles(
            min_age=min_age,
            max_age=max_age,
            gender=gender,
            city=city,
            tags=tags,
            skip=skip,
            limit=limit
        )
        return [ProfileResponse.model_validate(profile) for profile in profiles]

    async def get_profile_by_username(self, username: str) -> ProfileResponse:
        profile = await self.repository.get_by_username(username)
        if not profile:
            raise ProfileNotFoundException(username, by_username=True)
        return ProfileResponse.model_validate(profile)