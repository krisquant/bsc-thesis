from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.goal import GoalType, TimePeriod
from app.models.base import Base, TimestampMixin, UUIDMixin


class Goal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goals"

    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_type: Mapped[GoalType] = mapped_column(
        Enum(GoalType),
        nullable=False,
    )
    target: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Target value: distance in km, duration in minutes, or number of runs",
    )
    time_period: Mapped[TimePeriod] = mapped_column(
        Enum(TimePeriod),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="goals")
