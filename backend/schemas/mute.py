from pydantic import BaseModel, Field, ConfigDict




class MuteUserResponse(BaseModel):
    """Схема ответа при изменении статуса мута."""
    success: bool = Field(..., example=True)
    message: str = Field(..., example="Пользователь замучен")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Пользователь замучен"
            }
        }
    )


class MutedUsersListResponse(BaseModel):
    """Схема ответа со списком замученных пользователей."""
    muted_user_ids: list[int] = Field(..., example=[2, 5, 10])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "muted_user_ids": [2, 5, 10]
            }
        }
    )