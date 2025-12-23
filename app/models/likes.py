from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel
    from app.models.users import UserModel
    from app.models.profiles import ProfileModel


class LikeModel(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # ✅ Кто лайкнул
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # ✅ Кого лайкнули (профиль)
    liked_profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    
    # ✅ Уникальная комбинация: один пользователь может лайкнуть один профиль только один раз
    __table_args__ = (
        UniqueConstraint('user_id', 'liked_profile_id', name='unique_user_liked_profile'),
    )
    
    # ✅ Связи
    user: Mapped["UserModel"] = relationship(back_populates="likes_made")
    liked_profile: Mapped["ProfileModel"] = relationship(back_populates="liked_by_users")
    
    # ✅ Для обратной совместимости (если нужно)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, default=1)
    role: Mapped["RoleModel"] = relationship(back_populates="likes")
