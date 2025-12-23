from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
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

router = APIRouter(prefix="/profiles", tags=["profiles"])


# ✅ НОВОЕ: Криейт профиль авторизованному пользователю
@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    username: str,
    age: int,
    gender: str,
    city: str,
    photo: str,
    description: str,
    tags: str = "",
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание профиля для текущего пользователя
    
    - **username**: Никнейм пользователя
    - **age**: Возраст
    - **gender**: Пол (строка 'мале' или 'female')
    - **city**: Город
    - **photo**: URL фотографии
    - **description**: Описание профиля
    - **tags**: Теги (опционально)
    """
    try:
        # ✅ Проверяем что профиль еще не сохранен
        existing_profile_stmt = select(ProfileModel).where(
            ProfileModel.user_id == current_user_id
        )
        existing_profile = await db.scalar(existing_profile_stmt)
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="У вас уже есть профиль"
            )
        
        # ✅ Создаем ProfileCreate с user_id и role_id
        profile_data = ProfileCreate(
            user_id=current_user_id,
            username=username,
            age=age,
            gender=gender,
            city=city,
            photo=photo,
            description=description,
            tags=tags,
            role_id=1  # ✅ Обычные пользователи
        )
        
        service = ProfileService(db)
        return await service.create_profile(profile_data)
    except HTTPException:
        raise
    except ProfileAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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


@router.get("/role/{role_id}", response_model=List[ProfileResponse])
async def get_profiles_by_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    return await service.get_profiles_by_role(role_id)
