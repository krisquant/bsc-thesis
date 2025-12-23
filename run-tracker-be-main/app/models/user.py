from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    gender: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    height: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    weight: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )

    goals = relationship("Goal", back_populates="user")
    runs = relationship("Run", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
