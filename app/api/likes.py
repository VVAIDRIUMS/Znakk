from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.likes import LikeCreate, LikeUpdate, LikeResponse
from app.schemas.profiles import ProfileResponse
from app.services.likes import LikeService
from app.services.profiles import ProfileService
from app.exceptions import LikeNotFoundException, LikeAlreadyExistsException
from app.api.dependencies import get_current_user, DBDep
from app.schemas.users import UserResponse
from app.database.db_manager import DBManager

router = APIRouter(prefix="/likes", tags=["likes"])


# ✅ НОВОЕ: Лайк с проверкой профиля
@router.post("/", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def create_like(
    like_data: LikeCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: DBManager = Depends(get_db)
):
    """
    Поставить лайк на профиль
    
    Можно только если у пользователя есть собственный профиль
    """
    profile_service = ProfileService(db.session)
    
    # ✅ Провераем что у пользователя есть профиль
    user_profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Сначала создайте свой профиль"
        )
    
    # ✅ Нельзя лайкнуть свой одн профиль
    if user_profile.id == like_data.liked_profile_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя лайкнуть свой профиль"
        )
    
    service = LikeService(db.session)
    try:
        return await service.create_like(like_data, current_user.id)
    except LikeAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# ✅ НОВОЕ: Получить профили которым САМ нользователь поставил лайк
@router.get("/my-likes", response_model=List[ProfileResponse])
async def get_my_likes(
    current_user: UserResponse = Depends(get_current_user),
    db: DBManager = Depends(get_db)
):
    """
    Профили которым я поставил лайк
    """
    service = LikeService(db.session)
    return await service.get_profiles_i_liked(current_user.id)


# ✅ НОВОЕ: Получить профили которые лайкнули МЕНЯ
@router.get("/who-liked-me", response_model=List[ProfileResponse])
async def get_who_liked_me(
    current_user: UserResponse = Depends(get_current_user),
    db: DBManager = Depends(get_db)
):
    """
    Профили которые лайкнули мой профиль
    """
    profile_service = ProfileService(db.session)
    
    # Находим профиль пользователя
    my_profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not my_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    service = LikeService(db.session)
    return await service.get_profiles_that_liked_me(my_profile.id)


# ✅ НОВОЕ: Удалить лайк по profile_id
@router.delete("/{liked_profile_id}")
async def delete_like(
    liked_profile_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: DBManager = Depends(get_db)
):
    """
    Удалить лайк с профиля
    """
    service = LikeService(db.session)
    try:
        return await service.delete_like(current_user.id, liked_profile_id)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Старые endpoints (двигаются для обратной совместимости)

@router.get("/", response_model=List[LikeResponse])
async def get_all_likes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: DBManager = Depends(get_db)
):
    service = LikeService(db.session)
    return await service.get_all_likes(skip, limit)


@router.get("/{like_id}", response_model=LikeResponse)
async def get_like(
    like_id: int,
    db: DBManager = Depends(get_db)
):
    service = LikeService(db.session)
    try:
        return await service.get_like(like_id)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/profile/{profile_id}", response_model=LikeResponse)
async def get_like_by_profile(
    profile_id: int,
    db: DBManager = Depends(get_db)
):
    service = LikeService(db.session)
    try:
        return await service.get_like_by_profile(profile_id)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{like_id}", response_model=LikeResponse)
async def update_like(
    like_id: int,
    like_data: LikeUpdate,
    db: DBManager = Depends(get_db)
):
    service = LikeService(db.session)
    try:
        return await service.update_like(like_id, like_data)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/role/{role_id}", response_model=List[LikeResponse])
async def get_likes_by_role(
    role_id: int,
    db: DBManager = Depends(get_db)
):
    service = LikeService(db.session)
    return await service.get_likes_by_role(role_id)
