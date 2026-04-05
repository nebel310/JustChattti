from pydantic import BaseModel, Field, ConfigDict




class FCMTokenRegisterRequest(BaseModel):
    """Схема запроса для регистрации FCM-токена."""
    fcm_token: str = Field(..., max_length=512, description="FCM-токен устройства")
    device_id: str | None = Field(None, max_length=256, description="Идентификатор устройства (опционально)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fcm_token": "fKjH... (длинная строка)",
                "device_id": "device_123"
            }
        }
    )


class FCMTokenUnregisterRequest(BaseModel):
    """Схема запроса для удаления FCM-токена."""
    fcm_token: str = Field(..., max_length=512, description="FCM-токен устройства")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fcm_token": "fKjH..."
            }
        }
    )


class FCMTokenRegisterResponse(BaseModel):
    """Схема ответа при успешной регистрации токена."""
    success: bool = Field(..., example=True)
    message: str = Field(..., example="FCM-токен успешно зарегистрирован")


class FCMTokenUnregisterResponse(BaseModel):
    """Схема ответа при успешном удалении токена."""
    success: bool = Field(..., example=True)
    message: str = Field(..., example="FCM-токен успешно удалён")