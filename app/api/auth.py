from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from jose import JWTError, jwt
from app.config import settings

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
    InvalidPasswordException,
    UserNotFoundException
)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 схема для токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ НОВАЯ ФУНКЦИЯ - получение ID пользователя из токена
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Извлечь ID пользователя из JWT токена
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        print(f"Registering user: {user_data.email}")
        return await service.register_user(user_data)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {str(e)}"
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
        print(f"Authenticating user: {login_data.email}")
        return await service.authenticate_user(login_data)
    except InvalidCredentialsException as e:
        print(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login error: {str(e)}"
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
        print(f"Authenticating user (JSON): {login_data.email}")
        return await service.authenticate_user(login_data)
    except InvalidCredentialsException as e:
        print(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login error: {str(e)}"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление токена
    """
    service = AuthService(db)
    try:
        return await service.refresh_token(current_user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error refreshing token: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user_id: int = Depends(get_current_user_id),
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
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error changing password: {str(e)}"
        )


# ✅ ОСНОВНОЙ ЭНДПОИНТ - получение текущего пользователя
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    Требует JWT токена в Authorization заголовке
    """
    service = AuthService(db)
    try:
        return await service.get_current_user(current_user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting user: {str(e)}"
        )


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