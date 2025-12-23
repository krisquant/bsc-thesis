from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class CreatedAtMixin:
    """
    Mixin that adds a created_at timestamp column to the model.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )


class UpdatedAtMixin:
    """
    Mixin that adds an updated_at timestamp column to the model.
    """

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """
    Mixin that combines created_at and updated_at timestamp functionality.
    """

    pass


class UUIDMixin:
    """
    Mixin that adds a UUID primary key column to the model.
    """

    uuid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )


class BaseModel(Base):  # type: ignore
    """
    Base class for SQLAlchemy models with a helper method for dictionary conversion.
    This class is marked as abstract so it isn’t mapped to a table directly.
    """

    __abstract__ = True

    def to_dict(self, exclude: set = None) -> dict:  # type:ignore
        """
        Convert the model instance to a dictionary representation,
        excluding any columns specified in the `exclude` set.
        """
        exclude = exclude or set()
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in exclude
        }
