from datetime import datetime
from datetime import timezone

from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database import Model




class FileOrm(Model):
    """Модель файла"""
    __tablename__ = 'files'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]  # UUID в MinIO
    original_name: Mapped[str]
    filetype: Mapped[str]  # 'image', 'video', 'audio', 'document'
    filesubtype: Mapped[str] # голосовое (да/нет), аватарка (да/нет)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )