from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.user_filters import (
    UserFilterCreate, 
    UserFilterUpdate, 
    UserFilterResponse,
    FilterStatsResponse,
    BulkFilterCreate
)
from app.services.user_filters import UserFilterService
from app.exceptions import (
    UserFilterNotFoundException,
    UserFilterAlreadyExistsException,
    InvalidFilterDataException
)

router = APIRouter(prefix="/user-filters", tags=["user-filters"])


@router.post("/", response_model=UserFilterResponse, status_code=status.HTTP_201_CREATED)
async def create_filter(
    filter_data: UserFilterCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.create_filter(filter_data)
    except UserFilterAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except InvalidFilterDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk", response_model=List[UserFilterResponse], status_code=status.HTTP_201_CREATED)
async def create_filters_bulk(
    bulk_data: BulkFilterCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.create_filters_bulk(bulk_data)
    except UserFilterAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=List[UserFilterResponse])
async def get_all_filters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_all_filters(skip, limit)


@router.get("/{filter_id}", response_model=UserFilterResponse)
async def get_filter(
    filter_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.get_filter(filter_id)
    except UserFilterNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/user/{user_id}", response_model=UserFilterResponse)
async def get_filter_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.get_filter_by_user(user_id)
    except UserFilterNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{filter_id}", response_model=UserFilterResponse)
async def update_filter(
    filter_id: int,
    filter_data: UserFilterUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.update_filter(filter_id, filter_data)
    except UserFilterNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserFilterAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/{filter_id}")
async def delete_filter(
    filter_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.delete_filter(filter_id)
    except UserFilterNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/user/{user_id}")
async def delete_filter_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    try:
        return await service.delete_filter_by_user(user_id)
    except UserFilterNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/role/{role_id}", response_model=List[UserFilterResponse])
async def get_filters_by_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_filters_by_role(role_id)


@router.get("/search/", response_model=List[UserFilterResponse])
async def search_filters(
    gender_filter: Optional[str] = Query(None, max_length=20),
    city_filter: Optional[str] = Query(None, max_length=30),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.search_filters(
        gender_filter=gender_filter,
        city_filter=city_filter,
        skip=skip,
        limit=limit
    )


@router.get("/gender/{gender}", response_model=List[UserFilterResponse])
async def get_filters_by_gender(
    gender: str,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_filters_by_gender(gender)


@router.get("/city/{city}", response_model=List[UserFilterResponse])
async def get_filters_by_city(
    city: str,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_filters_by_city(city)


@router.get("/stats/", response_model=FilterStatsResponse)
async def get_filter_stats(
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_filter_stats()


@router.get("/apply/{user_id}/{gender}/{city}", response_model=List[UserFilterResponse])
async def get_users_by_filter_criteria(
    user_id: int,
    gender: str,
    city: str,
    db: AsyncSession = Depends(get_db)
):
    service = UserFilterService(db)
    return await service.get_users_by_filter_criteria(gender, city)