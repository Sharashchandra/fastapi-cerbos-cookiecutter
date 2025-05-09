from datetime import datetime
from functools import partial

from sqlalchemy import ForeignKey, inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP


class Base(DeclarativeBase):
    def json(self, exclude_unset: bool = False, exclude: list = None):
        from fastapi.encoders import jsonable_encoder

        return jsonable_encoder(self, exclude=exclude, exclude_unset=exclude_unset)

    def dict(self, exclude_unset: bool = False, exclude: list = None):
        if exclude is None:
            exclude = []
        if exclude_unset:
            return {
                c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs
                if c.key not in exclude and getattr(self, c.key)
            }
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs if c.key not in exclude}


class AuditBase(Base):
    """
    Abstract base class that adds common columns to all tables
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now()
    )

    @declared_attr
    def created_by_user(cls):
        return relationship("User", foreign_keys=[cls.created_by_user_id], uselist=False)

    @declared_attr
    def updated_by_user(cls):
        return relationship("User", foreign_keys=[cls.updated_by_user_id], uselist=False)

    @declared_attr
    def created_by_user_id(cls):
        return mapped_column(ForeignKey("users_user.id", ondelete="SET NULL"), nullable=True)

    @declared_attr
    def updated_by_user_id(cls):
        return mapped_column(ForeignKey("users_user.id", ondelete="SET NULL"), nullable=True)


# Set Loading Strategy to "selectin"
relationship = partial(relationship, lazy="selectin")
