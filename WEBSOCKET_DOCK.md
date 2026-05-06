# WebSocket API чата

## Подключение
`ws://domain/ws?token=<JWT_ACCESS_TOKEN>`

После подключения клиент автоматически начинает получать все события, связанные с его чатами. Перед отправкой текущего JWT, надо бы его обновить. Срок жизни токенов указан в .env

---

## Сообщения от клиента к серверу

### `ping`
Проверка соединения.
```json
{
  "type": "ping"
}
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
  "metadata": null,
  "client_message_id": "my-unique-id-123"
}
```
- `chat_id` (int) — обязательное поле.
- `content` (string | null) — текст сообщения, максимум 5000 символов.
- `message_type` (string) — одно из: `"text"`, `"image"`, `"video"`, `"audio"`, `"voice"`, `"file"`.
- `file_id` (int | null) — ID загруженного файла, если сообщение содержит файл.
- `reply_to_id` (int | null) — ID сообщения, на которое отвечает данное.
- `metadata` (object | null) — дополнительные данные. Для `message_type: "voice"` обязательно поле `duration` (число, длительность в секундах).
- `client_message_id` (string | null) — произвольная строка для идентификации сообщения на клиенте (будет возвращена в `message_sent`).

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
Подтверждение доставки сообщений. Помечает сообщения как доставленные (`delivered`).
```json
{
  "type": "ack",
  "chat_id": 1,
  "message_ids": [1, 2, 3]
}
```
- `message_ids` — массив целых чисел, ID сообщений, которые пользователь получил.

### `read`
Подтверждение прочтения сообщений. Помечает сообщения как прочитанные (`read`).
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
Сигналы WebRTC (offer, answer, candidate, hangup). Звонки реализованы как заглушки, сигналы просто пересылаются.
```json
{
  "type": "webrtc",
  "target_user_id": 2,
  "call_id": 1,
  "signal_type": "offer",
  "data": {
    "sdp": "v=0\r\no=- 123456 2 IN IP4 127.0.0.1..."
  }
}
```
- `target_user_id` (int) — ID пользователя, которому предназначен сигнал.
- `call_id` (int | null) — ID звонка (может отсутствовать).
- `signal_type` (string) — тип сигнала: `"offer"`, `"answer"`, `"candidate"`, `"hangup"`.
- `data` (object) — содержимое сигнала (зависит от типа).

---

## Сообщения от сервера к клиенту

### `pong`
Ответ на `ping`.
```json
{
  "type": "pong"
}
```

### `message`
Новое сообщение в чате.
**Отправляется:** всем участникам чата, находящимся онлайн, сразу после сохранения в БД (при отправке через WebSocket или REST).
```json
{
  "type": "message",
  "message": {
    "id": 100,
    "chat_id": 1,
    "sender_id": 2,
    "sender_username": "user2",
    "sender_avatar_url": "http://{IP адрес сервера}:9000/files/uuid.jpg",
    "sender_avatar_id": null,
    "sender_metadata": null,
    "message_type": "text",
    "content": "Привет!",
    "file_id": null,
    "file_url": null,
    "reply_to_id": null,
    "status": "sent",
    "edited": false,
    "metadata": null,
    "client_message_id": "my-unique-id-123",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```
- `status` — одно из: `"sent"`, `"delivered"`, `"read"`.
- `sender_avatar_url` и `file_url` — строки или `null`.
- `sender_avatar_id` — ID аватара отправителя или `null`.
- `sender_metadata` — объект с дополнительной информацией о пользователе или `null`.
- `metadata` — объект с метаданными сообщения (например, `{"duration": 30.5}`) или `null`.
- `client_message_id` — строка, переданная клиентом при отправке, или `null`.

### `message_sent`
Подтверждение успешной отправки сообщения.
**Отправляется:** только отправителю.
```json
{
  "type": "message_sent",
  "message_id": 100,
  "status": "sent",
  "client_message_id": "my-unique-id-123"
}
```
- `client_message_id` — значение, полученное от клиента при отправке, или `null`.

### `message_edited`
Сообщение было отредактировано.
**Отправляется:** всем участникам чата.
```json
{
  "type": "message_edited",
  "message": {
    "id": 100,
    "chat_id": 1,
    "sender_id": 2,
    "sender_username": "user2",
    "sender_avatar_url": "http://minio:9000/files/uuid.jpg",
    "sender_avatar_id": null,
    "sender_metadata": null,
    "message_type": "text",
    "content": "Новый текст сообщения",
    "file_id": null,
    "file_url": null,
    "reply_to_id": null,
    "status": "sent",
    "edited": true,
    "metadata": null,
    "client_message_id": null,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:05:00Z"
  }
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
- `user_id` — ID пользователя, который подтвердил доставку.

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
- `user_id` — ID пользователя, который прочитал сообщения.

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
**Отправляется:** всем участникам всех общих чатов с этим пользователем.
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
  "data": {
    "sdp": "v=0\r\no=- 123456 2 IN IP4 127.0.0.1..."
  }
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

- Push-уведомления (FCM) отправляются только если получатель **офлайн** и **не замутил** отправителя. Проверки реализованы на бекенде.
- При активном WebSocket-соединении сообщения приходят всегда, даже если отправитель замучен.
- Отправлять сообщение можно как через вебсокет, так и через REST. Но лучше через REST, так как там мне проще следить за валидностью