from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.schemas.profiles import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.profiles import ProfileService
from app.exceptions import (
    ProfileNotFoundException, 
    ProfileAlreadyExistsException,
    InvalidProfileDataException
)
from app.api.dependencies import get_current_user_id
from app.models.profiles import ProfileModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profiles", tags=["profiles"])


# ✅ НОВОЕ: Криейт профиль авторизованному пользователю
@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    username: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    photo: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание профиля для текущего пользователя
    
    - **username**: Никнейм пользователя
    - **age**: Возраст
    - **gender**: Пол (строка 'male' или 'female')
    - **city**: Город
    - **photo**: URL фотографии
    - **description**: Описание профиля
    - **tags**: Теги (опционально)
    """
    try:
        logger.info(f"\ud83d\udcc4 Начинаем создание профиля for user_id={current_user_id}")
        logger.info(f"  username={username}")
        logger.info(f"  age={age}")
        logger.info(f"  gender={gender}")
        logger.info(f"  city={city}")
        logger.info(f"  photo={photo[:50]}...")
        logger.info(f"  description={description[:50]}...")
        logger.info(f"  tags={tags}")
        
        # ✅ Проверяем что профиль ещё не сохранен
        logger.info(f"\ud83d\udd0d Проверяем existing profile...")
        existing_profile_stmt = select(ProfileModel).where(
            ProfileModel.user_id == current_user_id
        )
        existing_profile = await db.scalar(existing_profile_stmt)
        
        if existing_profile:
            logger.warning(f"\u26a0\ufe0f Профиль user_id={current_user_id} уже есть")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="У вас уже есть профиль"
            )
        
        logger.info(f"\u2705 Нет existing profile - можно сохранять")
        
        # ✅ Проверяем данные
        logger.info(f"\ud83d\udd0d Проверяем данные...")
        if not all([username, age, gender, city, photo, description]):
            logger.error(f"\u274c Отсутствуют обязательные поля")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Все поля обязательные"
            )
        
        logger.info(f"\u2705 Все поля заполнены")
        
        # ✅ Проверяем возраст
        logger.info(f"\ud83d\udd0d Проверяем возраст...")
        try:
            age_int = int(age)
            logger.info(f"  age_int={age_int}")
            if age_int < 18 or age_int > 120:
                logger.error(f"\u274c Возраст {age_int} не в диапазоне 18-120")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Возраст должен быть от 18 до 120"
                )
        except ValueError as e:
            logger.error(f"\u274c Невозможно преобразовать возраст в целое: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Возраст должен быть числом"
            )
        
        logger.info(f"\u2705 Возраст верен")
        
        # ✅ Ок все хорошо, дальше сохраяем
        logger.info(f"\ud83d\udd0d Нормализуем данные...")
        profile_data = ProfileCreate(
            user_id=current_user_id,
            username=username.strip(),
            age=age_int,
            gender=gender.strip(),
            city=city.strip(),
            photo=photo.strip(),
            description=description.strip(),
            tags=tags.strip() if tags else "",
            role_id=1  # ✅ Обычные пользователи
        )
        
        logger.info(f"\ud83d\udc7b ProfileCreate объект составлен")
        
        # ✅ Отправляем в сервис
        logger.info(f"\ud83d\udd0d Отправляем в ProfileService...")
        service = ProfileService(db)
        result = await service.create_profile(profile_data)
        
        logger.info(f"\u2705 Профиль успешно сохранен: id={result.id}")
        return result
        
    except HTTPException as e:
        logger.error(f"\u274c HTTPException: status={e.status_code}, detail={e.detail}")
        raise
    except ProfileAlreadyExistsException as e:
        logger.error(f"\u274c ProfileAlreadyExistsException: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"\u274c Непредвиденная ошибка: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сервера: {str(e)}"
        )


# ✅ НОВОЕ: Получить все профили с фильтрами
@router.get("/", response_model=List[ProfileResponse])
async def get_all_profiles(
    city: Optional[str] = Query(None, max_length=30),
    gender: Optional[str] = Query(None, max_length=20),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все профили с опциональными фильтрами
    """
    service = ProfileService(db)
    
    if city or gender:
        return await service.search_profiles(
            gender=gender,
            city=city,
            skip=skip,
            limit=limit
        )
    
    return await service.get_all_profiles(skip, limit)


# ✅ НОВОЕ: Получить по никнейму (до получения по ID)
@router.get("/username/{username}", response_model=ProfileResponse)
async def get_profile_by_username(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.get_profile_by_username(username)
    except ProfileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ✅ НОВОЕ: Получить по user_id до получения по ID
@router.get("/user/{user_id}", response_model=ProfileResponse)
async def get_profile_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.get_profile_by_user_id(user_id)
    except ProfileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ✅ НОВОЕ: Получить по ID (апосле строк)
@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.get_profile(profile_id)
    except ProfileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ✅ ОБНОВЛЕНО: Обновление профиля
@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.update_profile(profile_id, profile_data)
    except ProfileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProfileAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# ✅ ОБНОвлено: Удаление профиля
@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.delete_profile(profile_id)
    except ProfileNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ✅ ОБНОвлено: Получить по role_id
@router.get("/role/{role_id}", response_model=List[ProfileResponse])
async def get_profiles_by_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    return await service.get_profiles_by_role(role_id)
