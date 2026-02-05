from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict




class UserSearchResult(BaseModel):
    """Результат поиска пользователей"""
    id: int = Field(..., example=2)
    username: str = Field(..., example="john_doe")
    avatar_id: Optional[int] = Field(None, example=5)
    avatar_url: Optional[str] = Field(None, example="http://minio:9000/images/uuid.jpg")
    bio: Optional[str] = Field(None, example="Привет, я Джон!")
    is_online: bool = Field(..., example=True)
    last_seen: datetime = Field(..., example="2024-01-01T12:00:00Z")
    
    model_config = ConfigDict(from_attributes=True)


class MessageSearchResult(BaseModel):
    """Результат поиска сообщений"""
    id: int = Field(..., example=1)
    chat_id: int = Field(..., example=1)
    sender_id: Optional[int] = Field(..., example=2)
    sender_username: Optional[str] = Field(..., example="john_doe")
    sender_avatar_url: Optional[str] = Field(None, example="http://minio:9000/images/uuid.jpg")
    message_type: str = Field(..., example="text")
    content: Optional[str] = Field(..., example="Привет, как дела?")
    file_id: Optional[int] = Field(None, example=5)
    file_url: Optional[str] = Field(None, example="http://minio:9000/images/uuid.jpg")
    reply_to_id: Optional[int] = Field(None, example=10)
    status: str = Field(..., example="read")
    edited: bool = Field(..., example=False)
    metadata: Optional[Dict[str, Any]] = Field(None, example={"duration": 30})
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    
    model_config = ConfigDict(from_attributes=True)


class UserSearchResponse(BaseModel):
    """Ответ на поиск пользователей"""
    users: List[UserSearchResult] = Field(
        ...,
        example=[
            {
                "id": 2,
                "username": "john_doe",
                "avatar_id": 5,
                "avatar_url": "http://minio:9000/images/uuid.jpg",
                "bio": "Привет, я Джон!",
                "is_online": True,
                "last_seen": "2024-01-01T12:00:00Z"
            }
        ]
    )
    total: int = Field(..., example=5)
    page: int = Field(..., example=1)
    page_size: int = Field(..., example=20)
    has_more: bool = Field(..., example=True)


class MessageSearchResponse(BaseModel):
    """Ответ на поиск сообщений"""
    messages: List[MessageSearchResult] = Field(
        ...,
        example=[
            {
                "id": 1,
                "chat_id": 1,
                "sender_id": 2,
                "sender_username": "john_doe",
                "message_type": "text",
                "content": "Привет, как дела?",
                "status": "read",
                "edited": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        ]
    )
    total: int = Field(..., example=15)
    page: int = Field(..., example=1)
    page_size: int = Field(..., example=20)
    has_more: bool = Field(..., example=True)


class UserSearchRequest(BaseModel):
    """Запрос на поиск пользователей"""
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        example="john",
        description="Часть username для поиска (регистронезависимый)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john"
            }
        }
    )


class MessageSearchRequest(BaseModel):
    """Запрос на поиск сообщений"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        example="привет",
        description="Текст для поиска в сообщениях"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "привет"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Схема ответа для ошибок"""
    detail: str = Field(..., example="Сообщение об ошибке")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Пользователь не является участником чата"
            }
        }
    )


class ValidationErrorResponse(BaseModel):
    """Схема ответа для ошибок валидации"""
    detail: List[Dict[str, Any]] = Field(
        ...,
        example=[
            {
                "type": "string_too_short",
                "loc": ["body", "username"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1}
            }
        ]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": [
                    {
                        "type": "string_too_short",
                        "loc": ["body", "username"],
                        "msg": "String should have at least 1 character",
                        "input": "",
                        "ctx": {"min_length": 1}
                    }
                ]
            }
        }
    )