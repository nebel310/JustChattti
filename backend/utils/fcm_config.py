import os
import logging

from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials




load_dotenv()


logger = logging.getLogger(__name__)

_firebase_initialized = False


def init_firebase() -> bool:
    """Инициализирует Firebase Admin SDK, если указан путь к credentials."""
    global _firebase_initialized

    if _firebase_initialized:
        return True

    credentials_path = os.getenv("FCM_CREDENTIALS_PATH")
    if not credentials_path:
        logger.warning("FCM_CREDENTIALS_PATH не задан в .env")
        return False

    if not os.path.exists(credentials_path):
        logger.warning(f"Файл credentials не найден: {credentials_path}")
        return False

    try:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK успешно инициализирован")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации Firebase: {e}")
        return False


def is_firebase_ready() -> bool:
    """Возвращает True, если Firebase инициализирован и готов к отправке."""
    return _firebase_initialized


init_firebase()