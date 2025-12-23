# app/services/users.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.repositories.users import UserRepository
from app.repositories.roles import RoleRepository
from app.schemas.users import (
    UserCreate, 
    UserUpdate, 
    UserResponse,
    UserWithRoleResponse,
    UserLogin,
    Token,
    PasswordChange,
    UserStatsResponse
)
from app.exceptions.users import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidPasswordException,
    UnauthorizedException
)

# Настройки JWT
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.role_repository = RoleRepository(session)

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
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> Optional[Any]:
        """Аутентификация пользователя"""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Создание нового пользователя"""
        # Проверяем, существует ли уже пользователь с таким email
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise UserAlreadyExistsException(user_data.email)
        
        # Проверяем существование роли
        role = await self.role_repository.get_by_id(user_data.role_id)
        if not role:
            raise ValueError(f"Role with id {user_data.role_id} does not exist")
        
        # Хэшируем пароль
        hashed_password = self.get_password_hash(user_data.password)
        
        # Создаем пользователя
        user = await self.repository.create({
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": user_data.is_active,
            "role_id": user_data.role_id
        })
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=datetime.now()
        )

    async def login_user(self, login_data: UserLogin) -> Token:
        """Вход пользователя"""
        user = await self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise UnauthorizedException("User account is disabled")
        
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

    async def get_current_user(self, token: str) -> Any:
        """Получение текущего пользователя из токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Could not validate credentials")
        except JWTError:
            raise UnauthorizedException("Could not validate credentials")
        
        user = await self.repository.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedException("User not found")
        
        if not user.is_active:
            raise UnauthorizedException("User account is disabled")
        
        return user

    async def get_user(self, user_id: int, include_role: bool = False) -> UserResponse | UserWithRoleResponse:
        """Получение пользователя по ID"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        if include_role:
            role = await self.role_repository.get_by_id(user.role_id)
            role_name = role.name if role else "Unknown"
            return UserWithRoleResponse(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                role_id=user.role_id,
                role_name=role_name,
                created_at=datetime.now()
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=datetime.now()
        )

    async def get_user_by_email(self, email: str) -> UserResponse:
        """Получение пользователя по email"""
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(email, by_email=True)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=datetime.now()
        )

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Получение всех пользователей"""
        users = await self.repository.get_all(skip, limit)
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                role_id=user.role_id,
                created_at=datetime.now()
            )
            for user in users
        ]

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Обновление пользователя"""
        # Проверяем существование пользователя
        existing_user = await self.repository.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundException(user_id)
        
        # Если обновляется email, проверяем его уникальность
        if user_data.email is not None:
            user_with_email = await self.repository.get_by_email(user_data.email)
            if user_with_email and user_with_email.id != user_id:
                raise UserAlreadyExistsException(user_data.email)
        
        # Если обновляется пароль, хэшируем его
        update_data = {}
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.password is not None:
            update_data["hashed_password"] = self.get_password_hash(user_data.password)
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        if user_data.role_id is not None:
            update_data["role_id"] = user_data.role_id
        
        user = await self.repository.update(user_id, update_data)
        if not user:
            raise UserNotFoundException(user_id)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=datetime.now()
        )

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Удаление пользователя"""
        success = await self.repository.delete(user_id)
        if not success:
            raise UserNotFoundException(user_id)
        return {"message": "User deleted successfully"}

    async def change_password(self, user_id: int, password_data: PasswordChange) -> Dict[str, Any]:
        """Смена пароля пользователя"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        # Проверяем текущий пароль
        if not self.verify_password(password_data.current_password, user.hashed_password):
            raise InvalidPasswordException("Current password is incorrect")
        
        # Хэшируем новый пароль
        hashed_password = self.get_password_hash(password_data.new_password)
        
        # Обновляем пароль
        await self.repository.update_password(user_id, hashed_password)
        return {"message": "Password changed successfully"}

    async def get_user_stats(self) -> UserStatsResponse:
        """Получение статистики пользователей"""
        stats = await self.repository.get_stats()
        return UserStatsResponse(**stats)