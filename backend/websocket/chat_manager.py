import json
from datetime import datetime
from datetime import timezone
from typing import Dict, Set, List, Optional

from fastapi import WebSocket, WebSocketDisconnect




class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.connection_users: Dict[WebSocket, int] = {}
        self.chat_subscriptions: Dict[int, Set[int]] = {}
    
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Устанавливает соединение с пользователем"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_users[websocket] = user_id
        
        # Уведомляем о подключении пользователя
        await self.broadcast_presence(user_id, True)
    
    
    def disconnect(self, websocket: WebSocket):
        """Закрывает соединение с пользователем"""
        user_id = self.connection_users.get(websocket)
        
        if user_id:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            del self.connection_users[websocket]
            
            # Уведомляем об отключении пользователя
            asyncio.create_task(self.broadcast_presence(user_id, False))
    
    
    async def subscribe_to_chat(self, websocket: WebSocket, chat_id: int):
        """Подписывает пользователя на обновления чата"""
        user_id = self.connection_users.get(websocket)
        
        if not user_id:
            return
        
        if chat_id not in self.chat_subscriptions:
            self.chat_subscriptions[chat_id] = set()
        
        self.chat_subscriptions[chat_id].add(user_id)
    
    
    async def unsubscribe_from_chat(self, websocket: WebSocket, chat_id: int):
        """Отписывает пользователя от обновлений чата"""
        user_id = self.connection_users.get(websocket)
        
        if not user_id:
            return
        
        if chat_id in self.chat_subscriptions:
            self.chat_subscriptions[chat_id].discard(user_id)
            
            if not self.chat_subscriptions[chat_id]:
                del self.chat_subscriptions[chat_id]
    
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправляет сообщение конкретному WebSocket соединению"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)
    
    
    async def send_to_user(self, message: dict, user_id: int):
        """Отправляет сообщение всем соединениям пользователя"""
        connections = self.active_connections.get(user_id, set())
        
        for connection in connections.copy():
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)
    
    
    async def broadcast_to_chat(
        self, 
        message: dict, 
        chat_id: int, 
        exclude_user_id: Optional[int] = None
    ):
        """Отправляет сообщение всем подписчикам чата"""
        user_ids = self.chat_subscriptions.get(chat_id, set())
        
        for user_id in user_ids:
            if user_id != exclude_user_id:
                await self.send_to_user(message, user_id)
    
    
    async def broadcast_presence(self, user_id: int, is_online: bool):
        """Рассылает информацию о статусе пользователя"""
        presence_msg = {
            "type": "presence",
            "user_id": user_id,
            "is_online": is_online,
            "last_seen": None if is_online else datetime.now(timezone.utc).isoformat()
        }
        
        # Отправляем всем, кто подписан на чаты с этим пользователем
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
        
        # Отправляем целевому пользователю
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
            
            # Сохраняем сообщение в БД
            message_data = MessageCreate(**data)
            message = await MessageRepository.send_message(message_data, user_id)
            
            # Рассылаем участникам чата
            chat_message = {
                "type": "message",
                "message": message
            }
            
            await self.broadcast_to_chat(
                chat_message, 
                data["chat_id"], 
                exclude_user_id=user_id
            )
            
            # Отправляем подтверждение отправителю
            await self.send_to_user({
                "type": "message_sent",
                "message_id": message["id"],
                "status": "sent"
            }, user_id)
            
        except Exception as e:
            await self.send_to_user({
                "type": "error",
                "error": str(e)
            }, user_id)


import asyncio
manager = ConnectionManager()