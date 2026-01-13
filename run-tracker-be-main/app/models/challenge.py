from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.run import Run
    from app.models.user import User


class Challenge(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "challenges"

    creator_id: Mapped[str] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False, index=True
    )
    source_run_id: Mapped[str] = mapped_column(
        ForeignKey("runs.uuid", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    source_run: Mapped["Run"] = relationship("Run", foreign_keys=[source_run_id])
    attempts: Mapped[List["ChallengeAttempt"]] = relationship(
        "ChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan"
    )


class ChallengeAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "challenge_attempts"

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.uuid", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[str] = mapped_column(
        ForeignKey("runs.uuid", ondelete="CASCADE"), nullable=False
    )
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    challenge: Mapped["Challenge"] = relationship(
        "Challenge", back_populates="attempts"
    )
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    run: Mapped["Run"] = relationship("Run", foreign_keys=[run_id])
