from pydantic import BaseModel, Field




class ErrorResponse(BaseModel):
    """Схема ответа для ошибок."""
    detail: str = Field(..., example="Сообщение об ошибке")


class ValidationErrorResponse(BaseModel):
    """Схема ответа для ошибок валидации."""
    detail: str = Field(..., example="Сообщение об ошибки валидации")