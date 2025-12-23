from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_
from app.models.users import UserModel
from app.schemas.users import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> UserModel:
        user = UserModel(
            email=user_data.email,
            hashed_password=user_data.password,
            is_active=user_data.is_active,
            role_id=user_data.role_id
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, user_id: int, user_data: UserUpdate, hashed_password: Optional[str] = None) -> Optional[UserModel]:
        update_data = user_data.dict(exclude_unset=True, exclude={"password"})
        
        if hashed_password:
            update_data["hashed_password"] = hashed_password
        
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_role_id(self, role_id: int) -> List[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.role_id == role_id)
        )
        return result.scalars().all()

    async def search_users(
        self,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserModel]:
        query = select(UserModel)
        
        if email:
            query = query.where(UserModel.email.ilike(f"%{email}%"))
        if is_active is not None:
            query = query.where(UserModel.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_users(self) -> List[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_active == True)
        )
        return result.scalars().all()

    async def get_inactive_users(self) -> List[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_active == False)
        )
        return result.scalars().all()

    async def get_stats(self) -> Dict[str, Any]:
        # Общее количество пользователей
        total_result = await self.session.execute(
            select(func.count()).select_from(UserModel)
        )
        total_users = total_result.scalar()

        # Активные пользователи
        active_result = await self.session.execute(
            select(func.count()).where(UserModel.is_active == True)
        )
        active_users = active_result.scalar()

        # Неактивные пользователи
        inactive_users = total_users - active_users

        # Пользователи по ролям
        role_result = await self.session.execute(
            select(
                UserModel.role_id,
                func.count(UserModel.id)
            )
            .group_by(UserModel.role_id)
        )
        users_by_role = {str(row[0]): row[1] for row in role_result.all()}

        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "inactive_users": inactive_users or 0,
            "users_by_role": users_by_role
        }

    async def update_password(self, user_id: int, hashed_password: str) -> Optional[UserModel]:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=hashed_password)
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def update_status(self, user_id: int, is_active: bool) -> Optional[UserModel]:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=is_active)
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()