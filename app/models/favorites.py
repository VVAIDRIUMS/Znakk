from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel


class FavoriteModel(Base):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(primary_key=True)
    favorite_profile_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    contact: Mapped[str] = mapped_column(String(20), nullable=False)
    is_mutual: Mapped[bool] = mapped_column(Boolean, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["RoleModel"] = relationship(back_populates="favorites")