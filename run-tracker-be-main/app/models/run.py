from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Run(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "runs"

    user_uuid: Mapped[str] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    duration: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Duration in minutes",
    )
    distance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Distance in km",
    )
    calories: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    route: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of route points: lat, lng, accuracy, altitude, speed, timestamp",
    )

    user: Mapped["User"] = relationship("User", back_populates="runs")
