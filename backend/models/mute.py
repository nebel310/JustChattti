from datetime import datetime
from datetime import timezone

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Model




class UserMuteOrm(Model):
    """Модель для хранения информации о замученных пользователях."""
    __tablename__ = 'user_mutes'

    id: Mapped[int] = mapped_column(primary_key=True)
    muted_by_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        comment="ID пользователя, который установил мут"
    )
    muted_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        comment="ID пользователя, которого замутили"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            'muted_by_user_id', 'muted_user_id',
            name='uq_user_mute_pair'
        ),
    )