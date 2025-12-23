from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.likes import LikeRepository
from app.schemas.likes import LikeCreate, LikeUpdate, LikeResponse
from app.exceptions import LikeNotFoundException, LikeAlreadyExistsException


class LikeService:
    def __init__(self, session: AsyncSession):
        self.repository = LikeRepository(session)

    async def create_like(self, like_data: LikeCreate) -> LikeResponse:
        # Проверяем, существует ли уже лайк с таким profile_id
        existing = await self.repository.get_by_profile_id(like_data.like_profile_id)
        if existing:
            raise LikeAlreadyExistsException(like_data.like_profile_id)
        
        like = await self.repository.create(like_data)
        return LikeResponse.model_validate(like)

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

    async def delete_like(self, like_id: int) -> dict:
        success = await self.repository.delete(like_id)
        if not success:
            raise LikeNotFoundException(like_id)
        return {"message": "Like deleted successfully"}

    async def get_likes_by_role(self, role_id: int) -> List[LikeResponse]:
        likes = await self.repository.get_by_role_id(role_id)
        return [LikeResponse.model_validate(like) for like in likes]

    async def get_mutual_likes(self) -> List[LikeResponse]:
        # Лайки, где я лайкнул профиль (me_liked = True)
        likes = await self.repository.get_mutual_likes()
        return [LikeResponse.model_validate(like) for like in likes]

    async def get_likes_by_status(self, me_liked: bool) -> List[LikeResponse]:
        # Лайки по статусу me_liked
        likes = await self.repository.get_likes_by_me_liked(me_liked)
        return [LikeResponse.model_validate(like) for like in likes]

    async def get_likes_i_made(self) -> List[LikeResponse]:
        # Лайки, которые я сделал
        return await self.get_likes_by_status(True)

    async def get_likes_i_received(self) -> List[LikeResponse]:
        # Лайки, которые я получил (где me_liked = False)
        return await self.get_likes_by_status(False)