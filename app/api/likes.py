from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.database.database import get_db
from app.models.likes import LikeModel
from app.models.profiles import ProfileModel
from app.models.users import UserModel
from app.schemas.likes import LikeCreate, LikeResponse
from app.schemas.profiles import ProfileResponse
from app.api.dependencies import get_current_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/likes", tags=["likes"])


# ✅ НОВОЕ: Добавить лайк
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
        logger.info(f"📬 Начинаем добавить лайк: user_id={current_user_id}, liked_profile_id={like_data.liked_profile_id}")
        
        # Проверяем что у пользователя есть профиль
        logger.info(f"🔍 Проверяем профиль текущего пользователя...")
        user_profile_stmt = select(ProfileModel).where(ProfileModel.user_id == current_user_id)
        user_profile = await db.scalar(user_profile_stmt)
        
        if not user_profile:
            logger.warning(f"⚠️ У пользователя {current_user_id} нет профиля")
            return {
                "success": False,
                "message": "Сначала создайте свой профиль"
            }
        
        logger.info(f"✅ Найден профиль текущего пользователя: id={user_profile.id}")
        
        # Нельзя лайкнуть свой профиль
        if user_profile.id == like_data.liked_profile_id:
            logger.warning(f"⚠️ Пользователь {current_user_id} пытается лайкнуть свой профиль")
            return {
                "success": False,
                "message": "Нельзя лайкнуть свой профиль"
            }
        
        logger.info(f"✅ то не его профиль")
        
        # Проверяем что профиль существует
        logger.info(f"🔍 Проверяем что профиль {like_data.liked_profile_id} существует...")
        liked_profile_stmt = select(ProfileModel).where(ProfileModel.id == like_data.liked_profile_id)
        liked_profile = await db.scalar(liked_profile_stmt)
        
        if not liked_profile:
            logger.warning(f"⚠️ Профиль {like_data.liked_profile_id} не найден")
            return {
                "success": False,
                "message": "Профиль не найден"
            }
        
        logger.info(f"✅ Профиль {like_data.liked_profile_id} найден")
        
        # Проверяем нет ли уже лайка
        logger.info(f"🔍 Проверяем али есть этот лайк...")
        existing_like_stmt = select(LikeModel).where(
            and_(
                LikeModel.user_id == current_user_id,
                LikeModel.liked_profile_id == like_data.liked_profile_id
            )
        )
        existing_like = await db.scalar(existing_like_stmt)
        
        if existing_like:
            logger.warning(f"⚠️ Лайк уже есть")
            return {
                "success": False,
                "message": "Вы уже лайкнули этот профиль"
            }
        
        logger.info(f"✅ Лайка ещё нет - сохраняем")
        
        # Сохраняем лайк
        new_like = LikeModel(
            user_id=current_user_id,
            liked_profile_id=like_data.liked_profile_id,
            role_id=1  # ✅ Нужен для совместимости с моделью
        )
        db.add(new_like)
        await db.commit()
        await db.refresh(new_like)
        
        logger.info(f"✅ Лайк успешно сохранен: id={new_like.id}")
        
        return {
            "success": True,
            "message": f"❤️ Вы лайкнули {liked_profile.username}!",
            "profile_id": like_data.liked_profile_id
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка в add_like: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
        logger.info(f"📬 Начинаем удалять лайк: user_id={current_user_id}, liked_profile_id={liked_profile_id}")
        
        # Находим лайк
        like_stmt = select(LikeModel).where(
            and_(
                LikeModel.user_id == current_user_id,
                LikeModel.liked_profile_id == liked_profile_id
            )
        )
        like = await db.scalar(like_stmt)
        
        if not like:
            logger.warning(f"⚠️ Лайк не найден")
            return {
                "success": False,
                "message": "Лайк не найден"
            }
        
        await db.delete(like)
        await db.commit()
        
        logger.info(f"✅ Лайк успешно удален")
        
        return {
            "success": True,
            "message": "Лайк удален"
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка в remove_like: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }


# ✅ НОВОЕ: Получить профили которым я лайкнул что я лайкнул
@router.get("/my-likes", response_model=List[ProfileResponse])
async def get_my_likes(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить профили которым я лайкнул
    """
    try:
        logger.info(f"📬 Начинаем загружать мои лайки: user_id={current_user_id}")
        
        # Находим все лайки текущего пользователя
        stmt = select(LikeModel).where(LikeModel.user_id == current_user_id)
        likes = await db.scalars(stmt)
        likes_list = list(likes)
        
        logger.info(f"📯 Найдено {len(likes_list)} лайков")
        
        profiles = []
        for like in likes_list:
            # Находим профиль который лайкнули
            profile_stmt = select(ProfileModel).where(ProfileModel.id == like.liked_profile_id)
            profile = await db.scalar(profile_stmt)
            if profile:
                profiles.append(ProfileResponse.model_validate(profile))
        
        logger.info(f"✅ Лайков загружено: {len(profiles)}")
        
        return profiles
    except Exception as e:
        logger.error(f"❌ Ошибка в get_my_likes: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []


# ✅ НОВОЕ: Получить профили которые лайкнули МНЕ
@router.get("/who-liked-me", response_model=List[ProfileResponse])
async def get_who_liked_me(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить профили которые лайкнули мой профиль
    """
    try:
        logger.info(f"📬 Начинаем получать кто лайкнул меня: user_id={current_user_id}")
        
        # Находим профиль текущего пользователя
        my_profile_stmt = select(ProfileModel).where(ProfileModel.user_id == current_user_id)
        my_profile = await db.scalar(my_profile_stmt)
        
        if not my_profile:
            logger.warning(f"⚠️ Профиль пользователя {current_user_id} не найден")
            return []
        
        logger.info(f"✅ Профиль пользователя найден: id={my_profile.id}")
        
        # Находим все лайки которые получил мой профиль
        stmt = select(LikeModel).where(LikeModel.liked_profile_id == my_profile.id)
        likes = await db.scalars(stmt)
        likes_list = list(likes)
        
        logger.info(f"📯 Количество лайков которые я получил: {len(likes_list)}")
        
        profiles = []
        for like in likes_list:
            # Находим профиль который лайкнул
            profile_stmt = select(ProfileModel).where(ProfileModel.user_id == like.user_id)
            profile = await db.scalar(profile_stmt)
            if profile:
                profiles.append(ProfileResponse.model_validate(profile))
        
        logger.info(f"✅ Профилей загружено: {len(profiles)}")
        
        return profiles
    except Exception as e:
        logger.error(f"❌ Ошибка в get_who_liked_me: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
        stmt = select(LikeModel).where(
            and_(
                LikeModel.user_id == current_user_id,
                LikeModel.liked_profile_id == profile_id
            )
        )
        like = await db.scalar(stmt)
        
        return {
            "liked": like is not None
        }
    except Exception:
        return {
            "liked": False
        }
