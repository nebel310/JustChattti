from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, field_validator




class ChatBase(BaseModel):
    """Базовая схема чата"""
    name: Optional[str] = Field(
        None, 
        max_length=100,
        example="Мой чат"
    )
    chat_type: str = Field(
        "private",
        example="private",
        description="Тип чата, всегда 'private'"
    )
    
    @field_validator('chat_type')
    def validate_chat_type(cls, v):
        if v != "private":
            raise ValueError("Только приватные чаты поддерживаются")
        return v


class ChatCreate(ChatBase):
    """Схема для создания чата"""
    participant_ids: List[int] = Field(
        ...,
        min_items=1,
        max_items=1,
        example=[2],
        description="Список ID участников (только один для приватного чата)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Чат с другом",
                "chat_type": "private",
                "participant_ids": [2]
            }
        }
    )


class ChatResponse(BaseModel):
    """Схема ответа с информацией о чате"""
    id: int = Field(..., example=1)
    name: Optional[str] = Field(None, example="Чат с другом")
    chat_type: str = Field(..., example="private")
    avatar_id: Optional[int] = Field(None, example=5)
    avatar_url: Optional[str] = Field(
        None, 
        example="http://minio:9000/images/uuid.jpg"
    )
    created_by_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    unread_count: int = Field(0, example=3)
    last_message: Optional[Dict[str, Any]] = Field(
        None,
        example={
            "id": 123,
            "content": "Привет!",
            "message_type": "text",
            "sender_id": 2,
            "created_at": "2024-01-01T12:05:00Z"
        }
    )
    participant_ids: List[int] = Field(
        default_factory=list,
        example=[1, 2],
        description="Список ID участников чата"
    )
    
    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(ChatResponse):
    """Схема ответа с детальной информацией о чате"""
    participants: List[Dict[str, Any]] = Field(
        default_factory=list,
        example=[
            {
                "id": 1,
                "user_id": 1,
                "username": "user1",
                "avatar_id": 3,
                "joined_at": "2024-01-01T12:00:00Z"
            }
        ]
    )


class MessageBase(BaseModel):
    """Базовая схема сообщения"""
    content: Optional[str] = Field(
        None,
        max_length=5000,
        example="Привет, как дела?"
    )
    message_type: str = Field(
        "text",
        example="text",
        description="Тип сообщения: text, image, video, audio, voice, file"
    )
    file_id: Optional[int] = Field(
        None,
        example=5,
        description="ID файла, если сообщение содержит файл"
    )
    reply_to_id: Optional[int] = Field(
        None,
        example=10,
        description="ID сообщения, на которое отвечаем"
    )
    
    @field_validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = {"text", "image", "video", "audio", "voice", "file"}
        if v not in allowed_types:
            raise ValueError(f"Тип сообщения должен быть одним из: {allowed_types}")
        return v


class MessageCreate(MessageBase):
    """Схема для создания сообщения"""
    chat_id: int = Field(..., example=1, description="ID чата")
    client_message_id: Optional[str] = Field(
        None,
        description="Произвольная строка клиента для идентификации сообщения"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chat_id": 1,
                "content": "Привет!",
                "message_type": "text",
                "file_id": None,
                "reply_to_id": None,
                "client_message_id": "my-temp-id-123"
            }
        }
    )


class MessageResponse(BaseModel):
    """Схема ответа с информацией о сообщении"""
    id: int = Field(..., example=1)
    chat_id: int = Field(..., example=1)
    sender_id: Optional[int] = Field(..., example=1)
    sender_username: Optional[str] = Field(..., example="user1")
    sender_avatar_url: Optional[str] = Field(None, example="http://minio:9000/images/uuid.jpg")
    sender_avatar_id: Optional[int] = Field(None, example=1)
    message_type: str = Field(..., example="text")
    content: Optional[str] = Field(None, example="Привет!")
    file_id: Optional[int] = Field(None, example=5)
    file_url: Optional[str] = Field(None, example="http://minio:9000/images/uuid.jpg")
    reply_to_id: Optional[int] = Field(None, example=10)
    status: str = Field(..., example="sent")
    edited: bool = Field(..., example=False)
    metadata: Optional[Dict[str, Any]] = Field(None, example={"duration": 30})
    client_message_id: Optional[str] = Field(
        None,
        description="Клиентский идентификатор, переданный при отправке"
    )
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    
    model_config = ConfigDict(from_attributes=True)


class MessagesResponse(BaseModel):
    """Схема ответа со списком сообщений"""
    messages: List[MessageResponse] = Field(
        ...,
        example=[
            {
                "id": 1,
                "chat_id": 1,
                "sender_id": 1,
                "sender_username": "user1",
                "message_type": "text",
                "content": "Привет!",
                "status": "read",
                "edited": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        ]
    )
    total: Optional[int] = Field(None, example=50)
    page: Optional[int] = Field(None, example=1)
    page_size: int = Field(..., example=20)
    has_more: bool = Field(..., example=True)
    next_cursor: Optional[str] = Field(None, example="...", description="Курсор для более старых сообщений")
    prev_cursor: Optional[str] = Field(None, example="...", description="Курсор для более новых сообщений")

class WebRTCMessage(BaseModel):
    """Схема для WebRTC сигналов"""
    type: str = Field(
        ...,
        example="offer",
        description="Тип сигнала: offer, answer, candidate, hangup"
    )
    target_user_id: int = Field(
        ...,
        example=2,
        description="ID пользователя, которому отправляется сигнал"
    )
    call_id: Optional[int] = Field(
        None,
        example=1,
        description="ID звонка"
    )
    data: Dict[str, Any] = Field(
        ...,
        example={"sdp": "v=0\\r\\no=- 123456 2 IN IP4 127.0.0.1\\r\\n..."}
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "offer",
                "target_user_id": 2,
                "call_id": 1,
                "data": {"sdp": "v=0\\r\\no=- 123456 2 IN IP4 127.0.0.1\\r\\n..."}
            }
        }
    )


class CallCreate(BaseModel):
    """Схема для создания звонка"""
    chat_id: int = Field(..., example=1, description="ID чата")
    call_type: str = Field(
        ...,
        example="audio",
        description="Тип звонка: audio или video"
    )
    
    @field_validator('call_type')
    def validate_call_type(cls, v):
        if v not in {"audio", "video"}:
            raise ValueError("Тип звонка должен быть 'audio' или 'video'")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chat_id": 1,
                "call_type": "audio"
            }
        }
    )


class CallResponse(BaseModel):
    """Схема ответа с информацией о звонке"""
    id: int = Field(..., example=1)
    chat_id: int = Field(..., example=1)
    initiator_id: int = Field(..., example=1)
    call_type: str = Field(..., example="audio")
    status: str = Field(..., example="ringing")
    started_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    ended_at: Optional[datetime] = Field(None, example="2024-01-01T12:05:00Z")
    
    model_config = ConfigDict(from_attributes=True)


class MarkAsReadRequest(BaseModel):
    """Схема для отметки сообщений как прочитанных"""
    message_ids: List[int] = Field(
        ...,
        min_items=1,
        example=[1, 2, 3],
        description="Список ID сообщений для отметки как прочитанные"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message_ids": [1, 2, 3]
            }
        }
    )


class TypingIndicator(BaseModel):
    """Схема для индикатора набора текста"""
    chat_id: int = Field(..., example=1, description="ID чата")
    user_id: int = Field(..., example=1, description="ID пользователя")
    is_typing: bool = Field(..., example=True, description="Флаг набора текста")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chat_id": 1,
                "user_id": 1,
                "is_typing": True
            }
        }
    )


class PresenceUpdate(BaseModel):
    """Схема для обновления статуса присутствия"""
    user_id: int = Field(..., example=1, description="ID пользователя")
    is_online: bool = Field(..., example=True, description="Флаг онлайн-статуса")
    last_seen: Optional[datetime] = Field(
        None,
        example="2024-01-01T12:00:00Z",
        description="Время последней активности"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "is_online": True,
                "last_seen": "2024-01-01T12:00:00Z"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Схема ответа для ошибок"""
    detail: str = Field(..., example="Сообщение об ошибке")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Чат не найден"
            }
        }
    )


class ValidationErrorResponse(BaseModel):
    """Схема ответа для ошибок валидации"""
    detail: List[Dict[str, Any]] = Field(
        ...,
        example=[
            {
                "type": "value_error",
                "loc": ["body", "chat_type"],
                "msg": "Только приватные чаты поддерживаются",
                "input": "group"
            }
        ]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "chat_type"],
                        "msg": "Только приватные чаты поддерживаются",
                        "input": "group"
                    }
                ]
            }
        }
    )