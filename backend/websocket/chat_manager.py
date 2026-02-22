import json
from datetime import datetime
from datetime import timezone
from typing import Dict, Set, Optional

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
import asyncio
import logging




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.connection_users: Dict[WebSocket, int] = {}
        self.chat_subscriptions: Dict[int, Set[int]] = {}


    async def connect(self, websocket: WebSocket, user_id: int):
        """Устанавливает соединение с пользователем"""
        await websocket.accept()
        logger.info(f"Пользователь {user_id} подключился")

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        self.connection_users[websocket] = user_id

        await self.update_user_status(user_id, True)

        await self.broadcast_presence(user_id, True)


    def disconnect(self, websocket: WebSocket):
        """Закрывает соединение с пользователем"""
        user_id = self.connection_users.get(websocket)
        if user_id:
            logger.info(f"Пользователь {user_id} отключился")
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            del self.connection_users[websocket]

            asyncio.create_task(self.update_user_status_and_notify(user_id))


    async def update_user_status_and_notify(self, user_id: int):
        """Обновляет статус пользователя и уведомляет других"""
        await self.update_user_status(user_id, False)
        await self.broadcast_presence(user_id, False)


    async def update_user_status(self, user_id: int, is_online: bool):
        """Обновляет статус пользователя в базе данных"""
        try:
            from repositories.auth import UserRepository
            await UserRepository.update_user_status(user_id, is_online)
            logger.info(f"Статус пользователя {user_id} обновлён: {'онлайн' if is_online else 'оффлайн'}")
        except Exception as e:
            logger.error(f"Ошибка обновления статуса пользователя {user_id}: {e}")


    async def subscribe_to_chat(self, websocket: WebSocket, chat_id: int):
        """Подписывает пользователя на обновления чата, если он является участником"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return

        try:
            from repositories.chat import ChatRepository
            chat = await ChatRepository.get_chat_detail(chat_id, user_id)
            if not chat:
                await self.send_to_user({
                    "type": "error",
                    "error": "Вы не являетесь участником этого чата"
                }, user_id)
                logger.warning(f"Пользователь {user_id} попытался подписаться на чат {chat_id}, но не участник")
                return
        except Exception as e:
            logger.error(f"Ошибка проверки участия в чате {chat_id}: {e}")
            await self.send_to_user({
                "type": "error",
                "error": "Внутренняя ошибка сервера"
            }, user_id)
            return

        if chat_id not in self.chat_subscriptions:
            self.chat_subscriptions[chat_id] = set()

        self.chat_subscriptions[chat_id].add(user_id)
        logger.info(f"Пользователь {user_id} подписался на чат {chat_id}")

        await self.send_to_user({
            "type": "subscribed",
            "chat_id": chat_id
        }, user_id)


    async def unsubscribe_from_chat(self, websocket: WebSocket, chat_id: int):
        """Отписывает пользователя от обновлений чата"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return

        if chat_id in self.chat_subscriptions:
            self.chat_subscriptions[chat_id].discard(user_id)
            logger.info(f"Пользователь {user_id} отписался от чата {chat_id}")
            if not self.chat_subscriptions[chat_id]:
                del self.chat_subscriptions[chat_id]


    async def send_to_user(self, message: dict, user_id: int):
        """Отправляет сообщение всем соединениям пользователя"""
        connections = self.active_connections.get(user_id, set())
        if not connections:
            logger.warning(f"Нет активных соединений для пользователя {user_id}")
            return

        try:
            encoded_message = jsonable_encoder(message)
        except Exception as e:
            logger.error(f"Ошибка кодирования сообщения для пользователя {user_id}: {e}")
            return

        for connection in connections.copy():
            try:
                await connection.send_json(encoded_message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                self.disconnect(connection)


    async def broadcast_to_chat(
        self,
        message: dict,
        chat_id: int,
        exclude_user_id: Optional[int] = None
    ):
        """Отправляет сообщение всем подписчикам чата"""
        user_ids = self.chat_subscriptions.get(chat_id, set())
        logger.info(f"Broadcast в чат {chat_id} для пользователей: {user_ids} (исключая {exclude_user_id})")
        for user_id in user_ids:
            if exclude_user_id is None or user_id != exclude_user_id:
                await self.send_to_user(message, user_id)


    async def broadcast_presence(self, user_id: int, is_online: bool):
        """Рассылает информацию о статусе пользователя"""
        presence_msg = {
            "type": "presence",
            "user_id": user_id,
            "is_online": is_online,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        for chat_id, user_ids in self.chat_subscriptions.items():
            if user_id in user_ids:
                for other_user_id in user_ids:
                    if other_user_id != user_id:
                        await self.send_to_user(presence_msg, other_user_id)


    async def handle_typing(self, websocket: WebSocket, data: dict):
        """Обрабатывает индикатор набора текста"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return

        typing_msg = {
            "type": "typing",
            "chat_id": data["chat_id"],
            "user_id": user_id,
            "is_typing": data["is_typing"]
        }
        await self.broadcast_to_chat(typing_msg, data["chat_id"], exclude_user_id=user_id)


    async def handle_webrtc_signal(self, websocket: WebSocket, data: dict):
        """Обрабатывает WebRTC сигналы"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return

        webrtc_msg = {
            "type": "webrtc",
            "from_user_id": user_id,
            **data
        }
        target_user_id = data.get("target_user_id")
        if target_user_id:
            await self.send_to_user(webrtc_msg, target_user_id)


    async def handle_message(self, websocket: WebSocket, data: dict):
        """Обрабатывает новое сообщение"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return

        try:
            from repositories.chat import MessageRepository
            from schemas.chat import MessageCreate

            logger.info(f"Получено сообщение от пользователя {user_id}: {data}")

            if data.get("message_type") == "voice":
                metadata = data.get("metadata", {})
                if "duration" not in metadata:
                    raise ValueError("Для голосовых сообщений требуется duration в metadata")
                try:
                    metadata["duration"] = float(metadata["duration"])
                except (ValueError, TypeError):
                    raise ValueError("duration должен быть числом")
                data["metadata"] = metadata

            message_data = MessageCreate(**data)
            message = await MessageRepository.send_message(message_data, user_id)
            logger.info(f"Сообщение сохранено в БД, id: {message['id']}")

            chat_message = {
                "type": "message",
                "message": message
            }
            await self.broadcast_to_chat(chat_message, data["chat_id"])  # exclude_user_id убран

            await self.send_to_user({
                "type": "message_sent",
                "message_id": message["id"],
                "status": "sent"
            }, user_id)

        except ValueError as e:
            logger.error(f"Ошибка валидации сообщения от {user_id}: {e}")
            await self.send_to_user({"type": "error", "error": str(e)}, user_id)
        except Exception as e:
            logger.error(f"Необработанная ошибка при обработке сообщения от {user_id}: {e}", exc_info=True)
            await self.send_to_user({"type": "error", "error": "Внутренняя ошибка сервера"}, user_id)
    
    
    async def handle_ack(self, websocket: WebSocket, data: dict):
        """Обрабатывает подтверждение получения сообщения (доставлено)"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return
        
        message_ids = data.get("message_ids", [])
        chat_id = data.get("chat_id")
        if not message_ids or not chat_id:
            return
        
        try:
            from repositories.chat import MessageRepository
            updated_ids = await MessageRepository.mark_as_delivered(message_ids, user_id, chat_id)
            if updated_ids:
                # Уведомляем всех участников чата о доставке (можно только отправителей, но для простоты - весь чат)
                await self.broadcast_to_chat({
                    "type": "delivered",
                    "message_ids": updated_ids,
                    "user_id": user_id  # кто подтвердил доставку
                }, chat_id)
        except Exception as e:
            logger.error(f"Ошибка при подтверждении доставки: {e}")


    async def handle_read_receipt(self, websocket: WebSocket, data: dict):
        """Обрабатывает подтверждение прочтения сообщений"""
        user_id = self.connection_users.get(websocket)
        if not user_id:
            return
        
        message_ids = data.get("message_ids", [])
        chat_id = data.get("chat_id")
        if not message_ids or not chat_id:
            return
        
        try:
            from repositories.chat import MessageRepository
            updated_map = await MessageRepository.mark_as_read(message_ids, user_id, chat_id)
            if updated_map:
                # Отправляем каждому отправителю уведомление о прочтении его сообщений
                for sender_id, msg_ids in updated_map.items():
                    await self.send_to_user({
                        "type": "read",
                        "message_ids": msg_ids,
                        "user_id": user_id  # кто прочитал
                    }, sender_id)
        except Exception as e:
            logger.error(f"Ошибка при подтверждении прочтения: {e}")


    async def notify_message_edited(self, message: dict):
        """Уведомляет участников чата об edited сообщении"""
        await self.broadcast_to_chat({
            "type": "message_edited",
            "message": message
        }, message["chat_id"])

    async def notify_message_deleted(self, chat_id: int, message_id: int):
        """Уведомляет участников чата об удалении сообщения"""
        await self.broadcast_to_chat({
            "type": "message_deleted",
            "message_id": message_id,
            "chat_id": chat_id
        }, chat_id)



manager = ConnectionManager()