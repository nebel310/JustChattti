from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.admin import SChangeRole, ChangeRoleResponse, SChangeStorageLimit, ChangeStorageLimitResponse
from schemas.base import ErrorResponse, ValidationErrorResponse
from repositories.admin import AdminRepository
from models.auth import UserOrm
from utils.security import get_current_admin_user




router = APIRouter(
    prefix="/auth",
    tags=['Пользователи']
)



@router.patch(
    "/role",
    response_model=ChangeRoleResponse,
    status_code=200,
    responses={
        400: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def change_user_role(
        change_data: SChangeRole,
        admin: UserOrm = Depends(get_current_admin_user)
    ):
    """
    Обновление роли пользователя
    
    Надо указать желаемую роль пользователя
    Эндпоинт примет только значение 'user' или 'admin'
    
    Доступно только администраторам
    """
    try:
        response_data = await AdminRepository.change_user_role(change_data)
        
        return ChangeRoleResponse(
            success=response_data.success,
            user_id=response_data.user_id,
            role=response_data.role
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.patch(
    "/user_storage_limit",
    response_model=ChangeStorageLimitResponse,
    status_code=200,
    responses={
        400: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def change_user_storage_limit(
        change_data: SChangeStorageLimit,
        admin: UserOrm = Depends(get_current_admin_user)
    ):
    """
    Эндпоинт для изменения лимита хранилища для пользователя
    
    Тоесть пользователь не может грузить файлов больше этого лимита
    """
    try:
        response_data = await AdminRepository.change_user_storage_limit(change_data)
        
        return ChangeStorageLimitResponse(
            success=response_data.success,
            user_id=response_data.user_id,
            storage_limit_bytes=response_data.storage_limit_bytes
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )