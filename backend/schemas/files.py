from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field




class SUploadFile(BaseModel):
    """Схема для указания метаданных при загрузке файла"""
    is_avatar: bool = False
    is_voice_message: bool = False


class SUploadFileResponse(BaseModel):
    """Схема ответа после загрузки файла"""
    success: bool = Field(..., example=True)
    file_id: int = Field(..., example=1)
    filename: str = Field(..., example='uuid.jpg')
    original_name: str = Field(..., example='original_name.jpg')
    filetype: str = Field(..., example='image')
    filesubtype: str = Field(..., example='avatar')
    uploaded_by_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")


class SFileResponse(BaseModel):
    """Схема ответа с информацией о файле"""
    id: int = Field(..., example=1)
    filename: str = Field(..., example='uuid.jpg')
    original_name: str = Field(..., example='original_name.jpg')
    filetype: str = Field(..., example='image')
    filesubtype: str = Field(..., example='avatar')
    uploaded_by_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    url: str | None = Field(None, example="https://minio.example.com/presigned-url")


class ErrorResponse(BaseModel):
    """Схема ответа для ошибок"""
    detail: str = Field(..., example="Сообщение об ошибке")