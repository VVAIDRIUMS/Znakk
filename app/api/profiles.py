from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.profiles import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.profiles import ProfileService
from app.exceptions import (
    ProfileNotFoundException, 
    ProfileAlreadyExistsException,
    InvalidProfileDataException
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.create_profile(profile_data)
    except ProfileAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ProfileResponse])
async def get_all_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
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


@router.get("/search/", response_model=List[ProfileResponse])
async def search_profiles(
    min_age: Optional[int] = Query(None, ge=18, le=120),
    max_age: Optional[int] = Query(None, ge=18, le=120),
    gender: Optional[str] = Query(None, max_length=20),
    city: Optional[str] = Query(None, max_length=30),
    tags: Optional[str] = Query(None, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    try:
        return await service.search_profiles(
            min_age=min_age,
            max_age=max_age,
            gender=gender,
            city=city,
            tags=tags,
            skip=skip,
            limit=limit
        )
    except InvalidProfileDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )