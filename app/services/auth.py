from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional

from app.schemas.users import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordChange
)
from app.models.users import UserModel
from app.repositories.users import UserRepository
from app.exceptions.users import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidPasswordException,
    UserNotFoundException
)

# Алиасы для обратной совместимости
SUserAdd = UserCreate

# Настройки JWT
SECRET_KEY = "your-secret-key-change-this-in-production"  # В продакшене используйте переменные окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хэширование пароля"""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        """Аутентификация пользователя"""
        # Ищем пользователя по email
        user = await self.user_repository.get_by_email(login_data.email)
        
        if not user:
            raise InvalidCredentialsException()
        
        # Проверяем пароль
        if not self.verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Проверяем активен ли пользователь
        if not user.is_active:
            raise InvalidCredentialsException("User account is disabled")
        
        # Создаем токен
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            user_id=user.id,
            role_id=user.role_id
        )

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException(user_data.email)
        
        # Хэшируем пароль
        hashed_password = self.get_password_hash(user_data.password)
        
        # Создаем пользователя
        
        user = await self.user_repository.create(user_data)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=datetime.now()
        )

    async def change_password(self, user_id: int, password_data: PasswordChange) -> dict:
        """Смена пароля пользователя"""
        # Получаем пользователя
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        # Проверяем текущий пароль
        if not self.verify_password(password_data.current_password, user.hashed_password):
            raise InvalidPasswordException("Current password is incorrect")
        
        # Хэшируем новый пароль
        new_hashed_password = self.get_password_hash(password_data.new_password)
        
        # Обновляем пароль
        await self.user_repository.update(user_id, {
            "hashed_password": new_hashed_password
        })
        
        return {"message": "Password changed successfully"}

    async def refresh_token(self, user_id: int) -> Token:
        """Обновление токена"""
        # Получаем пользователя
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        # Создаем новый токен
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            user_id=user.id,
            role_id=user.role_id
        )

    async def get_current_user(self, user_id: int) -> UserResponse:
        """Получение информации о текущем пользователе"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=getattr(user, 'created_at', datetime.now())
        )

    async def validate_token(self, token: str) -> dict:
        """Валидация токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise InvalidCredentialsException()
            
            return {"user_id": int(user_id), "email": payload.get("email")}
        except jwt.PyJWTError:
            raise InvalidCredentialsException()