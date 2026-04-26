import asyncio
import logging
from typing import Dict, Any, Optional

from repositories.fcm import FCMTokenRepository
from utils.fcm_config import is_firebase_ready




logger = logging.getLogger(__name__)


async def send_push_notification(
    user_id: int,
    title: str,
    body: str,
    data_payload: Optional[Dict[str, Any]] = None
) -> None:
    """Отправляет push-уведомление пользователю на все его устройства."""
    if not is_firebase_ready():
        logger.warning("Firebase не инициализирован, push-уведомление не отправлено")
        return

    tokens = await FCMTokenRepository.get_tokens_by_user(user_id)
    if not tokens:
        logger.info(f"Нет FCM-токенов для пользователя {user_id}")
        return

    try:
        from firebase_admin import messaging
    except ImportError:
        logger.error("firebase-admin не установлен")
        return

    if data_payload is None:
        data_payload = {}

    for token in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data_payload,
                token=token,
            )

            response = await asyncio.to_thread(messaging.send, message)
            logger.info(f"Push отправлен на токен {token[:10]}..., response: {response}")
        except messaging.UnregisteredError:
            logger.warning(f"Токен {token[:10]}... не зарегистрирован, удаляем")
            await FCMTokenRepository.remove_invalid_token(token)
        except Exception as e:
            logger.error(f"Ошибка отправки push на токен {token[:10]}...: {e}")