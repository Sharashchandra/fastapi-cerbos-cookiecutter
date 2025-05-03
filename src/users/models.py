from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP

from src.core.constants import TokenType
from src.database.base_class import Base, relationship


class User(Base):
    __tablename__ = "users_user"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    full_name: Mapped[Optional[str]] = mapped_column(nullable=True)

    is_active: Mapped[bool] = mapped_column(default=False)
    is_mfa_enabled: Mapped[bool] = mapped_column(default=True)
    email_verified: Mapped[bool] = mapped_column(default=False)

    is_blocked: Mapped[bool] = mapped_column(default=False, nullable=False)
    blocked_until: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    last_login: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now()
    )

    active_mfa_attempt: Mapped[Optional["MFAAttempt"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class MFAAttempt(Base):
    __tablename__ = "users_mfa_attempt"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    code: Mapped[str] = mapped_column(nullable=False)
    code_expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    incorrect_attempts_count: Mapped[int] = mapped_column(default=0, nullable=False)
    resend_count: Mapped[int] = mapped_column(default=0, nullable=False)

    user: Mapped["User"] = relationship(uselist=False, back_populates="active_mfa_attempt", cascade="all, delete")


class BlacklistedToken(Base):
    __tablename__ = "users_blacklisted_token"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(nullable=False)
    token_type: Mapped[TokenType] = mapped_column(
        ENUM(TokenType, create_type=True),
        nullable=False,
        default=TokenType.REFRESH,
    )
    blacklisted_on: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_by: Mapped["User"] = relationship(uselist=False, cascade="all, delete")
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users_user.id"), nullable=False)
