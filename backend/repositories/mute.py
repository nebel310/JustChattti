from typing import List

from sqlalchemy import select, delete

from database import new_session
from models.mute import UserMuteOrm




class MuteRepository:
    """Репозиторий для работы с мутами пользователей."""

    @classmethod
    async def mute_user(cls, muted_by_user_id: int, muted_user_id: int) -> bool:
        """Добавляет пользователя в список замученных. Возвращает True, если запись создана."""
        if muted_by_user_id == muted_user_id:
            raise ValueError("Нельзя замутить самого себя")

        async with new_session() as session:
            # Проверяем, нет ли уже такой записи
            existing_query = select(UserMuteOrm).where(
                UserMuteOrm.muted_by_user_id == muted_by_user_id,
                UserMuteOrm.muted_user_id == muted_user_id
            )
            existing_result = await session.execute(existing_query)
            if existing_result.scalar_one_or_none():
                return False  # Уже замучен

            mute_entry = UserMuteOrm(
                muted_by_user_id=muted_by_user_id,
                muted_user_id=muted_user_id
            )
            session.add(mute_entry)
            await session.commit()
            return True

    @classmethod
    async def unmute_user(cls, muted_by_user_id: int, muted_user_id: int) -> bool:
        """Удаляет пользователя из списка замученных. Возвращает True, если запись удалена."""
        async with new_session() as session:
            delete_query = delete(UserMuteOrm).where(
                UserMuteOrm.muted_by_user_id == muted_by_user_id,
                UserMuteOrm.muted_user_id == muted_user_id
            )
            result = await session.execute(delete_query)
            await session.commit()
            return result.rowcount > 0

    @classmethod
    async def is_muted(cls, muted_by_user_id: int, muted_user_id: int) -> bool:
        """Проверяет, замутил ли пользователь muted_by_user_id пользователя muted_user_id."""
        async with new_session() as session:
            query = select(UserMuteOrm.id).where(
                UserMuteOrm.muted_by_user_id == muted_by_user_id,
                UserMuteOrm.muted_user_id == muted_user_id
            )
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    @classmethod
    async def get_muted_users(cls, muted_by_user_id: int) -> List[int]:
        """Возвращает список ID пользователей, которых замутил данный пользователь."""
        async with new_session() as session:
            query = select(UserMuteOrm.muted_user_id).where(
                UserMuteOrm.muted_by_user_id == muted_by_user_id
            )
            result = await session.execute(query)
            return list(result.scalars().all())