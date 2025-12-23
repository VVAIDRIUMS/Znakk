from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel


class LikeModel(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    like_profile_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    contact: Mapped[str] = mapped_column(String(20), nullable=False)
    me_liked: Mapped[bool] = mapped_column(Boolean, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["RoleModel"] = relationship(back_populates="likes")