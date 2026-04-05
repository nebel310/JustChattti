from fastapi import APIRouter, Depends, HTTPException

from models.auth import UserOrm
from repositories.fcm import FCMTokenRepository
from schemas.fcm import (
    FCMTokenRegisterRequest,
    FCMTokenUnregisterRequest,
    FCMTokenRegisterResponse,
    FCMTokenUnregisterResponse
)
from schemas.base import ErrorResponse, ValidationErrorResponse
from utils.security import get_current_user




router = APIRouter(
    prefix="/fcm",
    tags=["Push уведомления"]
)


@router.post(
    "/register",
    response_model=FCMTokenRegisterResponse,
    status_code=200,
    responses={
        400: {"model": ValidationErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def register_fcm_token(
    request: FCMTokenRegisterRequest,
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Регистрация FCM-токена устройства.
    
    Токен привязывается к текущему пользователю.
    Если токен уже существует, обновляется его привязка.
    """
    try:
        await FCMTokenRepository.register_token(
            user_id=current_user.id,
            fcm_token=request.fcm_token,
            device_id=request.device_id
        )
        return FCMTokenRegisterResponse(
            success=True,
            message="FCM-токен успешно зарегистрирован"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete(
    "/unregister",
    response_model=FCMTokenUnregisterResponse,
    status_code=200,
    responses={
        400: {"model": ValidationErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def unregister_fcm_token(
    request: FCMTokenUnregisterRequest,
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаление FCM-токена устройства.
    
    Токен удаляется только если он принадлежит текущему пользователю.
    """
    try:
        deleted = await FCMTokenRepository.unregister_token(
            user_id=current_user.id,
            fcm_token=request.fcm_token
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="FCM-токен не найден")
        return FCMTokenUnregisterResponse(
            success=True,
            message="FCM-токен успешно удалён"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")