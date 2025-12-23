from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt
from typing import Optional
import bcrypt

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

# Настройки JWT
SECRET_KEY = "your-secret-key-change-this-in-production"  # В продакшене используйте переменные окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    def hash_password(self, password: str) -> str:
        """Хеширование пароля с использованием bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

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
            raise InvalidCredentialsException("User not found")
        
        # Проверяем пароль
        if not self.verify_password(login_data.password, user.password):
            raise InvalidCredentialsException("Invalid password")
        
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
            raise UserAlreadyExistsException(f"User with email {user_data.email} already exists")
        
        # Хешируем пароль
        hashed_password = self.hash_password(user_data.password)
        
        # Создаем пользователя
        user = await self.user_repository.add(
            email=user_data.email,
            password=hashed_password,
            role_id=user_data.role_id
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=user.created_at
        )

    async def change_password(self, user_id: int, password_data: PasswordChange) -> dict:
        """Смена пароля пользователя"""
        # Получаем пользователя
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        
        # Проверяем текущий пароль
        if not self.verify_password(password_data.current_password, user.password):
            raise InvalidPasswordException("Current password is incorrect")
        
        # Хешируем новый пароль
        new_hashed_password = self.hash_password(password_data.new_password)
        
        # Обновляем пароль
        await self.user_repository.update(user_id, {"password": new_hashed_password})
        
        return {"message": "Password changed successfully"}

    async def refresh_token(self, user_id: int) -> Token:
        """Обновление токена"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        
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
            raise UserNotFoundException(f"User with id {user_id} not found")
        
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
                raise InvalidCredentialsException("Invalid token")
            
            return {"user_id": int(user_id), "email": payload.get("email")}
        except jwt.PyJWTError:
            raise InvalidCredentialsException("Invalid token")
