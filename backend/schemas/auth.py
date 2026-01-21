from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field




class SUserRegister(BaseModel):
    """Схема для регистрации нового пользователя."""
    username: str
    password: str
    password_confirm: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "test-user",
                    "password": "securepassword123",
                    "password_confirm": "securepassword123"
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




class SUser(BaseModel):
    """Схема для отображения информации о пользователе."""
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "test-user",
                    "created_at": "2024-01-01T12:00:00Z"
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




class ErrorResponse(BaseModel):
    """Схема ответа для ошибок."""
    detail: str = Field(..., example="Сообщение об ошибке")




class ValidationErrorResponse(BaseModel):
    """Схема ответа для ошибок валидации."""
    detail: str = Field(..., example="Пользователь с таким username уже существует")




class SRefreshToken(BaseModel):
    """Схема получения refresh токена"""
    refresh: str = Field(..., example="eyJhbG...")