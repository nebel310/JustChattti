import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from websocket.chat_manager import manager
from utils.security import get_current_user_from_token




router = APIRouter()



@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """WebSocket endpoint для чата и WebRTC сигналов"""
    if not token:
        await websocket.close(code=1008, reason="Токен не предоставлен")
        return

    try:
        user = await get_current_user_from_token(token)

        if not user:
            await websocket.close(code=1008, reason="Неверный токен")
            return
    except Exception as e:
        print(f"Ошибка аутентификации WebSocket: {e}")
        await websocket.close(code=1008, reason="Ошибка аутентификации")
        return

    await manager.connect(websocket, user.id)

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "subscribe":
                chat_id = data.get("chat_id")

                if isinstance(chat_id, int):
                    await manager.subscribe_to_chat(websocket, chat_id)

            elif message_type == "unsubscribe":
                chat_id = data.get("chat_id")

                if isinstance(chat_id, int):
                    await manager.unsubscribe_from_chat(websocket, chat_id)

            elif message_type == "typing":
                await manager.handle_typing(websocket, data)

            elif message_type == "webrtc":
                await manager.handle_webrtc_signal(websocket, data)

            elif message_type == "message":
                await manager.handle_message(websocket, data)

            elif message_type == "presence":
                await manager.broadcast_presence(user.id, data.get("is_online", True))

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "ack":
                await manager.handle_ack(websocket, data)

            elif message_type == "read":
                await manager.handle_read_receipt(websocket, data)

            else:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Неизвестный тип сообщения: {message_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        print(f"Ошибка WebSocket: {e}")
        manager.disconnect(websocket)