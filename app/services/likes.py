from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.likes import LikeRepository
from app.repositories.profiles import ProfileRepository
from app.schemas.likes import LikeCreate, LikeUpdate, LikeResponse
from app.schemas.profiles import ProfileResponse
from app.models.profiles import ProfileModel
from app.exceptions import LikeNotFoundException, LikeAlreadyExistsException


class LikeService:
    def __init__(self, session: AsyncSession):
        self.repository = LikeRepository(session)
        self.session = session

    # ✅ НОВОЕ: Нормальное создание лайка с user_id
    async def create_like(self, like_data: LikeCreate, user_id: int) -> LikeResponse:
        """
        Создать лайк
        """
        # Проверям что лайк уже не существует
        existing = await self.repository.get_by_user_and_profile(user_id, like_data.liked_profile_id)
        if existing:
            raise LikeAlreadyExistsException(f"Вы уже лайкнули этот профиль")
        
        # Объединяем user_id с данными
        like_dict = like_data.dict()
        like_dict['user_id'] = user_id
        like_dict['role_id'] = 1  # Дефолтная роль
        
        like = await self.repository.create(LikeCreate(**like_dict))
        return LikeResponse.model_validate(like)

    # ✅ НОВОЕ: Получить профили которым я поставил лайк
    async def get_profiles_i_liked(self, user_id: int) -> List[ProfileResponse]:
        """
        Получить профили которым я поставил лайк
        """
        likes = await self.repository.get_by_user_id(user_id)
        
        # Отделяем профили из лайков
        profiles = []
        for like in likes:
            if like.liked_profile:
                profiles.append(ProfileResponse.model_validate(like.liked_profile))
        
        return profiles

    # ✅ НОВОЕ: Получить профили которые лайкнули мой профиль
    async def get_profiles_that_liked_me(self, my_profile_id: int) -> List[ProfileResponse]:
        """
        Получить профили которые лайкнули мой профиль
        """
        likes = await self.repository.get_by_liked_profile_id(my_profile_id)
        
        # Отделяем профили тех, кто нас лайкнул
        profiles = []
        for like in likes:
            # Предявляем к пользователю profile_repository
            profile_repo = ProfileRepository(self.session)
            user_profile = await profile_repo.get_by_user_id(like.user_id)
            if user_profile:
                profiles.append(ProfileResponse.model_validate(user_profile))
        
        return profiles

    # ✅ НОВОЕ: Удалить лайк по user_id и liked_profile_id
    async def delete_like(self, user_id: int, liked_profile_id: int) -> dict:
        """
        Удалить лайк
        """
        like = await self.repository.get_by_user_and_profile(user_id, liked_profile_id)
        if not like:
            raise LikeNotFoundException(f"Лайк не найден")
        
        success = await self.repository.delete(like.id)
        if not success:
            raise LikeNotFoundException(f"Не удалось удалить лайк")
        
        return {"message": "Лайк успешно удален"}

    # Старые методы (для обратной совместимости)

    async def get_like(self, like_id: int) -> LikeResponse:
        like = await self.repository.get_by_id(like_id)
        if not like:
            raise LikeNotFoundException(like_id)
        return LikeResponse.model_validate(like)

    async def get_like_by_profile(self, profile_id: int) -> LikeResponse:
        like = await self.repository.get_by_profile_id(profile_id)
        if not like:
            raise LikeNotFoundException(profile_id, by_profile=True)
        return LikeResponse.model_validate(like)

    async def get_all_likes(self, skip: int = 0, limit: int = 100) -> List[LikeResponse]:
        likes = await self.repository.get_all(skip, limit)
        return [LikeResponse.model_validate(like) for like in likes]

    async def update_like(self, like_id: int, like_data: LikeUpdate) -> LikeResponse:
        like = await self.repository.update(like_id, like_data)
        if not like:
            raise LikeNotFoundException(like_id)
        return LikeResponse.model_validate(like)

    async def get_likes_by_role(self, role_id: int) -> List[LikeResponse]:
        likes = await self.repository.get_by_role_id(role_id)
        return [LikeResponse.model_validate(like) for like in likes]
