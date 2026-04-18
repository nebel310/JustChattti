from datetime import datetime
from datetime import timezone
from enum import Enum

from sqlalchemy import ForeignKey, String, Text, Enum as SQLEnum, Boolean, Index, text
from sqlalchemy import DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database import Model




class ChatType(str, Enum):
    """Типы чатов"""
    PRIVATE = "private"


class MessageType(str, Enum):
    """Типы сообщений"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    FILE = "file"


class MessageStatus(str, Enum):
    """Статусы сообщений"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class ChatOrm(Model):
    """Модель чата"""
    __tablename__ = 'chats'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    chat_type: Mapped[ChatType] = mapped_column(
        SQLEnum(ChatType),
        default=ChatType.PRIVATE
    )
    avatar_id: Mapped[int | None] = mapped_column(
        ForeignKey('files.id', ondelete='SET NULL'), 
        nullable=True
    )
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class ChatParticipantOrm(Model):
    """Участник чата"""
    __tablename__ = 'chat_participants'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    last_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class MessageOrm(Model):
    """Сообщение в чате"""
    __tablename__ = 'messages'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='CASCADE')
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    message_type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType),
        default=MessageType.TEXT
    )
    content: Mapped[str] = mapped_column(Text, nullable=True)
    file_id: Mapped[int | None] = mapped_column(
        ForeignKey('files.id', ondelete='SET NULL'),
        nullable=True
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        ForeignKey('messages.id', ondelete='SET NULL'),
        nullable=True
    )
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus),
        default=MessageStatus.SENT
    )
    edited: Mapped[bool] = mapped_column(default=False)
    message_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        Index('idx_messages_chat_created_id', 'chat_id', 'created_at', 'id'),
        Index('idx_messages_content_gin', func.to_tsvector(text("'simple'"), text('content')), postgresql_using='gin')
    )


class CallOrm(Model):
    """Модель звонка WebRTC"""
    __tablename__ = 'calls'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='CASCADE')
    )
    initiator_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    call_type: Mapped[str] = mapped_column(String(20))  # audio, video
    status: Mapped[str] = mapped_column(String(20))  # ringing, active, ended
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class CallParticipantOrm(Model):
    """Участник звонка"""
    __tablename__ = 'call_participants'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey('calls.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )