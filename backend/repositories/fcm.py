from datetime import datetime, timezone
from typing import List

from sqlalchemy import select, update

from database import new_session
from models.fcm import UserFCMTokenOrm




class FCMTokenRepository:
    """Репозиторий для работы с FCM-токенами пользователей."""
    @classmethod
    async def register_token(cls, user_id: int, fcm_token: str, device_id: str | None = None) -> None:
        """Регистрирует или обновляет FCM-токен пользователя."""
        async with new_session() as session:
            existing_query = select(UserFCMTokenOrm).where(UserFCMTokenOrm.fcm_token == fcm_token)
            existing_result = await session.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            if existing:
                if existing.user_id != user_id:
                    raise ValueError("Токен уже принадлежит другому пользователю")
                existing.updated_at = datetime.now(timezone.utc)
                if device_id is not None:
                    existing.device_id = device_id
            else:
                new_token = UserFCMTokenOrm(
                    user_id=user_id,
                    fcm_token=fcm_token,
                    device_id=device_id,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(new_token)

            await session.commit()


    @classmethod
    async def unregister_token(cls, user_id: int, fcm_token: str) -> bool:
        """Удаляет FCM-токен пользователя. Возвращает True, если токен был удалён."""
        async with new_session() as session:
            query = select(UserFCMTokenOrm).where(
                UserFCMTokenOrm.user_id == user_id,
                UserFCMTokenOrm.fcm_token == fcm_token
            )
            result = await session.execute(query)
            token_orm = result.scalar_one_or_none()

            if not token_orm:
                return False

            await session.delete(token_orm)
            await session.commit()
            return True


    @classmethod
    async def get_tokens_by_user(cls, user_id: int) -> List[str]:
        """Возвращает список всех FCM-токенов пользователя."""
        async with new_session() as session:
            query = select(UserFCMTokenOrm.fcm_token).where(UserFCMTokenOrm.user_id == user_id)
            result = await session.execute(query)
            tokens = result.scalars().all()
            return list(tokens)


    @classmethod
    async def remove_invalid_token(cls, fcm_token: str) -> bool:
        """Удаляет невалидный FCM-токен из базы. Возвращает True, если токен был удалён."""
        async with new_session() as session:
            query = select(UserFCMTokenOrm).where(UserFCMTokenOrm.fcm_token == fcm_token)
            result = await session.execute(query)
            token_orm = result.scalar_one_or_none()

            if not token_orm:
                return False

            await session.delete(token_orm)
            await session.commit()
            return True