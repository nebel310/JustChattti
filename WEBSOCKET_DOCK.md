# WebSocket API чата

## Подключение
`ws://domain/ws?token=<JWT_ACCESS_TOKEN>`

После подключения клиент автоматически начинает получать все события, связанные с его чатами

---

## Сообщения от клиента к серверу

### `ping`
Проверка соединения.
```json
{ "type": "ping" }
```

### `message`
Отправка нового сообщения.
```json
{
  "type": "message",
  "chat_id": 1,
  "content": "Привет!",
  "message_type": "text",
  "file_id": null,
  "reply_to_id": null,
  "metadata": {}
}
```

### `typing`
Индикатор набора текста.
```json
{
  "type": "typing",
  "chat_id": 1,
  "is_typing": true
}
```

### `ack`
Подтверждение доставки сообщений (помечает как `delivered`).
```json
{
  "type": "ack",
  "chat_id": 1,
  "message_ids": [1, 2, 3]
}
```

### `read`
Подтверждение прочтения сообщений (помечает как `read`).
```json
{
  "type": "read",
  "chat_id": 1,
  "message_ids": [1, 2, 3]
}
```

### `presence`
Обновление статуса онлайн/офлайн.
```json
{
  "type": "presence",
  "is_online": true
}
```

### `webrtc`
Сигналы WebRTC (offer, answer, candidate, hangup).
Звонки реализованы как заглушки.
```json
{
  "type": "webrtc",
  "target_user_id": 2,
  "call_id": 1,
  "signal_type": "offer",
  "data": { "sdp": "..." }
}
```

---

## Сообщения от сервера к клиенту

### `pong`
Ответ на `ping`.
```json
{ "type": "pong" }
```

### `message`
Новое сообщение в чате.  
**Отправляется:** всем участникам чата, находящимся онлайн, сразу после сохранения в БД.
```json
{
  "type": "message",
  "message": {
    "id": 100,
    "chat_id": 1,
    "sender_id": 2,
    "content": "Привет!",
    "message_type": "text",
    "status": "sent",
    "created_at": "2024-01-01T12:00:00Z",
    ...
  }
}
```

### `message_sent`
Подтверждение успешной отправки сообщения (приходит только отправителю).
```json
{
  "type": "message_sent",
  "message_id": 100,
  "status": "sent"
}
```

### `message_edited`
Сообщение было отредактировано.  
**Отправляется:** всем участникам чата.
```json
{
  "type": "message_edited",
  "message": { ... }
}
```

### `message_deleted`
Сообщение было удалено.  
**Отправляется:** всем участникам чата.
```json
{
  "type": "message_deleted",
  "message_id": 100,
  "chat_id": 1
}
```

### `delivered`
Сообщения доставлены получателю.  
**Отправляется:** всем участникам чата после обработки `ack`.
```json
{
  "type": "delivered",
  "message_ids": [1, 2, 3],
  "user_id": 2
}
```

### `read`
Сообщения прочитаны получателем.  
**Отправляется:** отправителю(ям) этих сообщений после обработки `read`.
```json
{
  "type": "read",
  "message_ids": [1, 2, 3],
  "user_id": 2
}
```

### `typing`
Кто-то печатает в чате.  
**Отправляется:** всем участникам чата, кроме самого печатающего.
```json
{
  "type": "typing",
  "chat_id": 1,
  "user_id": 2,
  "is_typing": true
}
```

### `presence`
Статус пользователя изменился.  
**Отправляется:** всем участникам **всех общих чатов** с этим пользователем.
```json
{
  "type": "presence",
  "user_id": 2,
  "is_online": false,
  "last_seen": "2024-01-01T12:00:00Z"
}
```

### `webrtc`
Входящий WebRTC сигнал.  
**Отправляется:** конкретному пользователю, указанному в `target_user_id`.
```json
{
  "type": "webrtc",
  "from_user_id": 2,
  "target_user_id": 1,
  "call_id": 1,
  "signal_type": "offer",
  "data": { "sdp": "..." }
}
```

### `error`
Ошибка обработки запроса.
```json
{
  "type": "error",
  "error": "описание ошибки"
}
```

---

## Примечания

- **Push-уведомления (FCM)** отправляются только если получатель **офлайн** и **не замутил** отправителя.
- При активном WebSocket-соединении сообщения приходят всегда, даже если отправитель замучен.