# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.database import get_db
from app.schemas.users import (
    UserCreate, 
    UserUpdate, 
    UserResponse,
    UserWithRoleResponse,
    UserLogin,
    Token,
    PasswordChange
)
from app.services.users import UserService
from app.exceptions.users import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    service = UserService(db)
    try:
        return await service.create_user(user_data)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Вход пользователя"""
    service = UserService(db)
    try:
        return await service.login_user(login_data)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех пользователей"""
    service = UserService(db)
    return await service.get_all_users(skip, limit)


@router.get("/{user_id}", response_model=UserWithRoleResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по ID"""
    service = UserService(db)
    try:
        return await service.get_user(user_id, include_role=True)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление пользователя"""
    service = UserService(db)
    try:
        return await service.update_user(user_id, user_data)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя"""
    service = UserService(db)
    try:
        return await service.delete_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по email"""
    service = UserService(db)
    try:
        return await service.get_user_by_email(email)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db)
):
    """Смена пароля (требует аутентификации)"""
    # В реальном приложении здесь нужно получить текущего пользователя из токена
    current_user_id = 1  # Заглушка
    service = UserService(db)
    try:
        return await service.change_password(current_user_id, password_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/health")
async def users_health():
    """Проверка здоровья модуля пользователей"""
    return {"status": "healthy"}