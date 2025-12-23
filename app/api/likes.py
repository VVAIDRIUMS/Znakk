from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.likes import LikeCreate, LikeUpdate, LikeResponse
from app.services.likes import LikeService
from app.exceptions import LikeNotFoundException, LikeAlreadyExistsException

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def create_like(
    like_data: LikeCreate,
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    try:
        return await service.create_like(like_data)
    except LikeAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=List[LikeResponse])
async def get_all_likes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    return await service.get_all_likes(skip, limit)


@router.get("/{like_id}", response_model=LikeResponse)
async def get_like(
    like_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
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
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
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
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    try:
        return await service.update_like(like_id, like_data)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{like_id}")
async def delete_like(
    like_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    try:
        return await service.delete_like(like_id)
    except LikeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/role/{role_id}", response_model=List[LikeResponse])
async def get_likes_by_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    return await service.get_likes_by_role(role_id)


@router.get("/me/made", response_model=List[LikeResponse])
async def get_likes_i_made(
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    return await service.get_likes_i_made()


@router.get("/me/received", response_model=List[LikeResponse])
async def get_likes_i_received(
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    return await service.get_likes_i_received()


@router.get("/status/{me_liked}", response_model=List[LikeResponse])
async def get_likes_by_status(
    me_liked: bool,
    db: AsyncSession = Depends(get_db)
):
    service = LikeService(db)
    return await service.get_likes_by_status(me_liked)