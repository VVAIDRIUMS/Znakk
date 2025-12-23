from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.database.database import get_db
from app.schemas.users import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordChange
)
from app.services.auth import AuthService
from app.exceptions.users import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidPasswordException
)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 схема для токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    service = AuthService(db)
    try:
        print(f"{user_data=}")
        return await service.register_user(user_data)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка регистрации: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя (получение токена)
    """
    service = AuthService(db)
    
    # Создаем объект UserLogin из form_data
    login_data = UserLogin(
        email=form_data.username,  # OAuth2 использует username вместо email
        password=form_data.password
    )
    
    try:
        return await service.authenticate_user(login_data)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка входа: {str(e)}"
        )


@router.post("/login-json", response_model=Token)
async def login_user_json(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя через JSON (альтернатива OAuth2 форме)
    """
    service = AuthService(db)
    
    try:
        return await service.authenticate_user(login_data)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка входа: {str(e)}"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user_id: int = Depends(lambda: 1),  # Заглушка - в реальном приложении брать из токена
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление токена
    """
    service = AuthService(db)
    return await service.refresh_token(current_user_id)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user_id: int = Depends(lambda: 1),  # Заглушка
    db: AsyncSession = Depends(get_db)
):
    """
    Смена пароля
    """
    service = AuthService(db)
    try:
        return await service.change_password(current_user_id, password_data)
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка смены пароля: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: int = Depends(lambda: 1),  # Заглушка
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    """
    service = AuthService(db)
    return await service.get_current_user(current_user_id)


@router.post("/logout")
async def logout_user():
    """
    Выход пользователя
    """
    return {"message": "Successfully logged out"}


@router.get("/health")
async def auth_health():
    """
    Проверка здоровья модуля аутентификации
    """
    return {"status": "healthy"}