from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Achievement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "achievements"

    user_uuid: Mapped[str] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(1024),
        nullable=True,
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    achievement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of achievement e.g. GOAL_COMPLETION, MILESTONE",
    )
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional data e.g. goal_id, run_id",
    )

    user: Mapped["User"] = relationship("User", back_populates="achievements")
