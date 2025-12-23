from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.favorites import FavoriteCreate, FavoriteUpdate, FavoriteResponse
from app.services.favorites import FavoriteService
from app.exceptions import FavoriteNotFoundException, FavoriteAlreadyExistsException

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    favorite_data: FavoriteCreate,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    try:
        return await service.create_favorite(favorite_data)
    except FavoriteAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=List[FavoriteResponse])
async def get_all_favorites(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    return await service.get_all_favorites(skip, limit)


@router.get("/{favorite_id}", response_model=FavoriteResponse)
async def get_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    try:
        return await service.get_favorite(favorite_id)
    except FavoriteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/profile/{profile_id}", response_model=FavoriteResponse)
async def get_favorite_by_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    try:
        return await service.get_favorite_by_profile(profile_id)
    except FavoriteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: int,
    favorite_data: FavoriteUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    try:
        return await service.update_favorite(favorite_id, favorite_data)
    except FavoriteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{favorite_id}")
async def delete_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    try:
        return await service.delete_favorite(favorite_id)
    except FavoriteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/role/{role_id}", response_model=List[FavoriteResponse])
async def get_favorites_by_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = FavoriteService(db)
    return await service.get_favorites_by_role(role_id)