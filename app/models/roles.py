# В models/roles.py добавьте relationship для user_filters
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.profiles import ProfileModel
    from app.models.favorites import FavoriteModel
    from app.models.likes import LikeModel
    from app.models.user_filters import User_filterModel


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List["UserModel"]] = relationship(back_populates="role")
    profiles: Mapped[List["ProfileModel"]] = relationship(back_populates="role")
    favorites: Mapped[List["FavoriteModel"]] = relationship(back_populates="role")
    likes: Mapped[List["LikeModel"]] = relationship(back_populates="role")
    user_filters: Mapped[List["User_filterModel"]] = relationship(back_populates="role")