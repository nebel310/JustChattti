from enum import Enum
from pydantic import BaseModel, ConfigDict, Field




class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SChangeRole(BaseModel):
    """Схема для изменения роли пользователя"""
    user_id: int
    new_user_role: UserRole

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "new_user_role": "admin"
                }
            ]
        }
    )
    

class SChangeStorageLimit(BaseModel):
    """Схема для изменения лимита хранилища для конкретного пользователя"""
    user_id: int
    new_storage_limit_bytes: int = Field(gt=0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "new_storage_limit_bytes": 2147483648
                }
            ]
        }
    )


class ChangeRoleResponse(BaseModel):
    """Схема ответа по изменению роли пользователя"""
    success: bool = Field(..., example=True)
    user_id: int = Field(..., example=1)
    role: str = Field(..., example="admin")
    

class ChangeStorageLimitResponse(BaseModel):
    """Схема ответа по изменению лимита хранилища пользователя"""
    success: bool = Field(..., example=True)
    user_id: int = Field(..., example=1)
    storage_limit_bytes: int = Field(..., example=2147483648)