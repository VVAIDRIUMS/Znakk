from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.favorites import FavoriteRepository
from app.schemas.favorites import FavoriteCreate, FavoriteUpdate, FavoriteResponse
from app.exceptions import FavoriteNotFoundException, FavoriteAlreadyExistsException


class FavoriteService:
    def __init__(self, session: AsyncSession):
        self.repository = FavoriteRepository(session)

    async def create_favorite(self, favorite_data: FavoriteCreate) -> FavoriteResponse:
        # Проверяем, существует ли уже запись с таким profile_id
        existing = await self.repository.get_by_profile_id(favorite_data.favorite_profile_id)
        if existing:
            raise FavoriteAlreadyExistsException(favorite_data.favorite_profile_id)
        
        favorite = await self.repository.create(favorite_data)
        return FavoriteResponse.model_validate(favorite)

    async def get_favorite(self, favorite_id: int) -> FavoriteResponse:
        favorite = await self.repository.get_by_id(favorite_id)
        if not favorite:
            raise FavoriteNotFoundException(favorite_id)
        return FavoriteResponse.model_validate(favorite)

    async def get_favorite_by_profile(self, profile_id: int) -> FavoriteResponse:
        favorite = await self.repository.get_by_profile_id(profile_id)
        if not favorite:
            raise FavoriteNotFoundException(profile_id, by_profile=True)
        return FavoriteResponse.model_validate(favorite)

    async def get_all_favorites(self, skip: int = 0, limit: int = 100) -> List[FavoriteResponse]:
        favorites = await self.repository.get_all(skip, limit)
        return [FavoriteResponse.model_validate(fav) for fav in favorites]

    async def update_favorite(self, favorite_id: int, favorite_data: FavoriteUpdate) -> FavoriteResponse:
        favorite = await self.repository.update(favorite_id, favorite_data)
        if not favorite:
            raise FavoriteNotFoundException(favorite_id)
        return FavoriteResponse.model_validate(favorite)

    async def delete_favorite(self, favorite_id: int) -> dict:
        success = await self.repository.delete(favorite_id)
        if not success:
            raise FavoriteNotFoundException(favorite_id)
        return {"message": "Favorite deleted successfully"}

    async def get_favorites_by_role(self, role_id: int) -> List[FavoriteResponse]:
        favorites = await self.repository.get_by_role_id(role_id)
        return [FavoriteResponse.model_validate(fav) for fav in favorites]