"""SQLAlchemy base declarative model."""

from __future__ import annotations

import datetime as dt
from typing import Any
import uuid

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> str:
    """Generate a standard UUID string."""
    return str(uuid.uuid4())


def utc_now() -> dt.datetime:
    """Generate timezone-aware UTC datetime."""
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    """Base class for all SlickFit database models."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model attributes to a dictionary."""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }
