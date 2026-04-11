from fastapi import APIRouter, Depends, HTTPException, Path

from models.auth import UserOrm
from repositories.mute import MuteRepository
from schemas.mute import MuteUserResponse, MutedUsersListResponse
from schemas.base import ErrorResponse
from utils.security import get_current_user




router = APIRouter(
    prefix="/users/me/muted",
    tags=["Мут пользователей"]
)


@router.post(
    "/{user_id}",
    response_model=MuteUserResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Замутить пользователя"
)
async def mute_user(
    user_id: int = Path(..., description="ID пользователя, которого нужно замутить"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Добавляет указанного пользователя в список замученных.
    После этого push-уведомления от этого пользователя не будут приходить.
    """
    try:
        created = await MuteRepository.mute_user(current_user.id, user_id)
        if created:
            return MuteUserResponse(success=True, message="Пользователь замучен")
        else:
            return MuteUserResponse(success=False, message="Пользователь уже был замучен")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{user_id}",
    response_model=MuteUserResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Пользователь не был замучен"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Размутить пользователя"
)
async def unmute_user(
    user_id: int = Path(..., description="ID пользователя, которого нужно размутить"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет указанного пользователя из списка замученных.
    """
    try:
        deleted = await MuteRepository.unmute_user(current_user.id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Пользователь не был замучен")
        return MuteUserResponse(success=True, message="Пользователь размучен")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/",
    response_model=MutedUsersListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Получить список замученных пользователей"
)
async def get_muted_users(
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список ID пользователей, которых текущий пользователь замутил.
    """
    try:
        muted_ids = await MuteRepository.get_muted_users(current_user.id)
        return MutedUsersListResponse(muted_user_ids=muted_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))