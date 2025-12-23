from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.database.models import Like, Profile, User
from app.schemas.likes import LikeCreate, LikeResponse
from app.schemas.profiles import ProfileResponse
from app.api.dependencies import get_current_user_id
from app.exceptions import LikeNotFoundException

router = APIRouter(prefix="/likes", tags=["likes"])


# ✅ НОВОЕ: Поставить лайк
@router.post("/add", response_model=dict, status_code=status.HTTP_200_OK)
async def add_like(
    like_data: LikeCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Поставить лайк на профиль
    
    - **liked_profile_id**: ID профиля, который лайкнуть
    """
    try:
        # Проверим что пользователь имеет профиль
        user_profile_stmt = select(Profile).where(Profile.user_id == current_user_id)
        user_profile = await db.scalar(user_profile_stmt)
        
        if not user_profile:
            return {
                "success": False,
                "message": "Сначала создайте свой профиль"
            }
        
        # Нельзя лайкнуть свой профиль
        if user_profile.id == like_data.liked_profile_id:
            return {
                "success": False,
                "message": "Нельзя лайкнуть свой профиль"
            }
        
        # Проверим что профиль существует
        liked_profile_stmt = select(Profile).where(Profile.id == like_data.liked_profile_id)
        liked_profile = await db.scalar(liked_profile_stmt)
        
        if not liked_profile:
            return {
                "success": False,
                "message": "Профиль не найден"
            }
        
        # Проверим нет ли уже лайка
        existing_like_stmt = select(Like).where(
            Like.user_id == current_user_id,
            Like.liked_profile_id == like_data.liked_profile_id
        )
        existing_like = await db.scalar(existing_like_stmt)
        
        if existing_like:
            return {
                "success": False,
                "message": "Вы уже лайкнули этот профиль"
            }
        
        # Сохраняем лайк
        new_like = Like(
            user_id=current_user_id,
            liked_profile_id=like_data.liked_profile_id
        )
        db.add(new_like)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Вы лайкнули {liked_profile.username}",
            "profile_id": like_data.liked_profile_id
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }


# ✅ НОВОЕ: Удалить лайк
@router.post("/remove/{liked_profile_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def remove_like(
    liked_profile_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить лайк с профиля
    """
    try:
        # Находим лайк
        like_stmt = select(Like).where(
            Like.user_id == current_user_id,
            Like.liked_profile_id == liked_profile_id
        )
        like = await db.scalar(like_stmt)
        
        if not like:
            return {
                "success": False,
                "message": "Лайк не найден"
            }
        
        await db.delete(like)
        await db.commit()
        
        return {
            "success": True,
            "message": "Лайк удален"
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }


# ✅ НОВОЕ: Получить профили которым я лайкнул
@router.get("/my-likes", response_model=List[ProfileResponse])
async def get_my_likes(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить профили которым я лайкнул
    """
    try:
        # Находим все лайки текущего пользователя
        stmt = select(Like).where(Like.user_id == current_user_id)
        likes = await db.scalars(stmt)
        
        profiles = []
        for like in likes:
            # Находим профиль который лайкнули
            profile_stmt = select(Profile).where(Profile.id == like.liked_profile_id)
            profile = await db.scalar(profile_stmt)
            if profile:
                profiles.append(ProfileResponse.model_validate(profile))
        
        return profiles
    except Exception as e:
        return []


# ✅ НОВОЕ: Получить ко мне лайкнули
@router.get("/who-liked-me", response_model=List[ProfileResponse])
async def get_who_liked_me(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить профили которые лайкнули МЕНЯ
    """
    try:
        # Находим профиль текущего пользователя
        my_profile_stmt = select(Profile).where(Profile.user_id == current_user_id)
        my_profile = await db.scalar(my_profile_stmt)
        
        if not my_profile:
            return []
        
        # Находим все лайки которые получил мой профиль
        stmt = select(Like).where(Like.liked_profile_id == my_profile.id)
        likes = await db.scalars(stmt)
        
        profiles = []
        for like in likes:
            # Находим профиль который лайкнул
            profile_stmt = select(Profile).where(Profile.user_id == like.user_id)
            profile = await db.scalar(profile_stmt)
            if profile:
                profiles.append(ProfileResponse.model_validate(profile))
        
        return profiles
    except Exception as e:
        return []


# ✅ НОВОЕ: Проверить был ли лайк на этот профиль
@router.get("/check/{profile_id}", response_model=dict)
async def check_like(
    profile_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Проверить был ли лайк на специфичный профиль
    """
    try:
        stmt = select(Like).where(
            Like.user_id == current_user_id,
            Like.liked_profile_id == profile_id
        )
        like = await db.scalar(stmt)
        
        return {
            "liked": like is not None
        }
    except Exception:
        return {
            "liked": False
        }


# ✅ НОВОЕ: Неавторизованные запросы - просим на регистрацию

@router.get("/my-likes", response_model=dict)
async def get_my_likes_unauthorized():
    """
    Получить лайки с авторизацией (fallback)
    """
    return {
        "success": False,
        "message": "Пожалуйста авторизуйтесь”
    }


@router.get("/who-liked-me", response_model=dict)
async def get_who_liked_me_unauthorized():
    """
    Получить ко мне с авторизацией (fallback)
    """
    return {
        "success": False,
        "message": "Пожалуйста авторизуйтесь"
    }
