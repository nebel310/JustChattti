from datetime import date
from datetime import datetime
from datetime import timezone

from sqlalchemy import Date, ForeignKey, String, DateTime, JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database import Model




class UserOrm(Model):
    """Модель пользователя в системе."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str]
    avatar_id: Mapped[int | None] = mapped_column(ForeignKey('files.id', ondelete='SET NULL'), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(250), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_online: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    
    # В это поле в каком то формате будет вставать
    # какая то дополнительная информация о пользователе в формате: ключ-значение
    user_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True) 


class RefreshTokenOrm(Model):
    """Модель refresh токена для аутентификации."""
    __tablename__ = 'refresh_tokens'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )


class BlacklistedTokenOrm(Model):
    """Модель черного списка токенов."""
    __tablename__ = 'blacklisted_tokens'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )