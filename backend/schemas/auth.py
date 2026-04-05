from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator




class SUserRegister(BaseModel):
    """Схема для регистрации нового пользователя."""
    username: str
    password: str
    password_confirm: str
    user_metadata: dict | None = None  # <-- добавлено

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "test-user",
                    "password": "securepassword123",
                    "password_confirm": "securepassword123",
                    "user_metadata": {"example_key": "example_value1", "damn": "nmad"}
                }
            ]
        }
    )


class SUserLogin(BaseModel):
    """Схема для входа в систему."""
    username: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "test-user",
                    "password": "securepassword123"
                }
            ]
        }
    )


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SUser(BaseModel):
    """Схема для отображения информации о пользователе."""
    id: int
    username: str
    avatar_id: int | None = None
    bio: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    is_online: bool
    last_seen: datetime
    created_at: datetime
    user_metadata: dict | None = None
    role: UserRole
    storage_used_bytes: int = Field(..., example=0)
    storage_limit_bytes: int = Field(..., example=1073741824)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "test-user",
                    "avatar_id": 123,
                    "bio": "Привет! Я новый пользователь",
                    "gender": "male",
                    "birth_date": "1990-01-01",
                    "is_online": True,
                    "role": UserRole.USER,
                    "storage_used_bytes" : 0,
                    "storage_limit_bytes" : 1073741824,
                    "last_seen": "2024-01-01T12:00:00Z",
                    "created_at": "2024-01-01T12:00:00Z",
                    "user_metadata": {"theme": "dark"}
                }
            ]
        }
    )


class SPublicUser(BaseModel):
    """Схема для публичной информации о пользователе."""
    id: int
    username: str
    avatar_id: int | None = None
    bio: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    is_online: bool
    last_seen: datetime
    created_at: datetime
    user_metadata: dict | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "test-user",
                    "avatar_id": 123,
                    "bio": "Привет! Я новый пользователь",
                    "gender": "male",
                    "birth_date": "1990-01-01",
                    "is_online": True,
                    "last_seen": "2024-01-01T12:00:00Z",
                    "created_at": "2024-01-01T12:00:00Z",
                    "user_metadata": {"theme": "dark"}
                }
            ]
        }
    )


class SUserStatus(BaseModel):
    """Схема для статуса пользователя."""
    user_id: int
    username: str
    is_online: bool
    last_seen: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "username": "test-user",
                    "is_online": True,
                    "last_seen": "2024-01-01T12:00:00Z"
                }
            ]
        }
    )


class SUserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""
    avatar_id: int | None = None
    bio: str | None = Field(None, max_length=250)
    gender: str | None = None
    birth_date: date | None = None
    user_metadata: dict | None = None

    @field_validator('bio')
    def validate_bio_length(cls, v):
        if v is not None and len(v) > 250:
            raise ValueError('Био не может превышать 250 символов')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "avatar_id": 123,
                    "bio": "Новое био пользователя",
                    "gender": "female",
                    "birth_date": "1995-05-15",
                    "user_metadata": {"theme": "light"}
                }
            ]
        }
    )


class RegisterResponse(BaseModel):
    """Схема ответа для успешной регистрации."""
    success: bool = Field(..., example=True)
    user_id: int = Field(..., example=1)
    message: str = Field(..., example="Регистрация прошла успешно")


class LoginResponse(BaseModel):
    """Схема ответа для успешного входа."""
    success: bool = Field(..., example=True)
    message: str = Field(..., example="Вы вошли в аккаунт")
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., example="bearer")


class RefreshResponse(BaseModel):
    """Схема ответа для обновления токена."""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., example="bearer")


class LogoutResponse(BaseModel):
    """Схема ответа для выхода из системы."""
    success: bool = Field(..., example=True)


class SRefreshToken(BaseModel):
    """Схема получения refresh токена"""
    refresh: str = Field(..., example="eyJhbG...")