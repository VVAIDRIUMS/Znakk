from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.roles import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsersResponse
from app.services.roles import RoleService
from app.exceptions import (
    RoleNotFoundException, 
    RoleAlreadyExistsException,
    RoleHasUsersException
)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        return await service.create_role(role_data)
    except RoleAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=List[RoleResponse])
async def get_all_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    return await service.get_all_roles(skip, limit)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    include_users: bool = Query(False, description="Включить информацию о пользователях"),
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        if include_users:
            return await service.get_role_with_users(role_id)
        return await service.get_role(role_id)
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/name/{name}", response_model=RoleResponse)
async def get_role_by_name(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        return await service.get_role_by_name(name)
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        return await service.update_role(role_id, role_data)
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RoleAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        return await service.delete_role(role_id)
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RoleHasUsersException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/", response_model=List[RoleResponse])
async def search_roles(
    name: str = Query(..., min_length=1, max_length=50, description="Название роли для поиска"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    return await service.search_roles(name, skip, limit)


@router.get("/{role_id}/with-users", response_model=RoleWithUsersResponse)
async def get_role_with_users(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = RoleService(db)
    try:
        return await service.get_role_with_users(role_id)
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )