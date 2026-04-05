from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path

from models.auth import UserOrm
from repositories.auth import UserRepository
from schemas.auth import LoginResponse
from schemas.auth import LogoutResponse
from schemas.auth import SRefreshToken
from schemas.auth import RefreshResponse
from schemas.auth import RegisterResponse
from schemas.auth import SUser
from schemas.auth import SPublicUser
from schemas.auth import SUserStatus
from schemas.auth import SUserUpdate
from schemas.auth import SUserLogin
from schemas.auth import SUserRegister
from schemas.base import ErrorResponse, ValidationErrorResponse
from utils.security import create_access_token
from utils.security import get_current_user
from utils.security import oauth2_scheme




router = APIRouter(
    prefix="/auth",
    tags=['Пользователи']
)



@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    responses={
        400: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def register_user(user_data: SUserRegister):
    """
    Регистрация нового пользователя.
    
    Пароль и подтверждение пароля должны совпадать.
    username должен быть уникальным.
    """
    try:
        user_id = await UserRepository.register_user(user_data)
        
        return RegisterResponse(
            success=True,
            user_id=user_id,
            message="Регистрация прошла успешно"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный username или пароль"},
        500: {"model": ErrorResponse}
    }
)
async def login_user(login_data: SUserLogin):
    """
    Вход в систему с получением токенов доступа.
    
    При успехе возвращает access_token и refresh_token.
    Access токен используется для доступа к защищенным эндпоинтам.
    Refresh токен используется для получения нового access токена.
    """
    try:
        user = await UserRepository.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(status_code=400, detail="Неверный username или пароль")
        
        # Обновляем статус пользователя как онлайн
        await UserRepository.update_user_status(user.id, True)
        
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = await UserRepository.create_refresh_token(user.id)
        
        return LoginResponse(
            success=True,
            message="Вы вошли в аккаунт",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
        
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail="Внутренняя ошибка сервера"
    #     )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный refresh токен"},
        500: {"model": ErrorResponse}
    }
)
async def refresh_token(refresh_token_data: SRefreshToken):
    """
    Обновление access токена с помощью refresh токена.
    
    Refresh токен должен быть валидным и не истекшим.
    Возвращает новый access токен.
    """
    try:
        user = await UserRepository.get_user_by_refresh_token(refresh_token_data)
        
        if not user:
            raise HTTPException(status_code=400, detail="Неверный refresh токен")
        
        new_access_token = create_access_token(data={"sub": user.username})
        
        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse}
    }
)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Выход из системы.
    
    Токен добавляется в черный список.
    Refresh токен пользователя отзывается.
    Статус пользователя меняется на оффлайн.
    Требует валидный access токен.
    """
    try:
        await UserRepository.add_to_blacklist(token)
        await UserRepository.revoke_refresh_token(current_user.id)
        await UserRepository.update_user_status(current_user.id, False)
        
        return LogoutResponse(success=True)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/me",
    response_model=SUser,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse}
    }
)
async def get_current_user_info(current_user: UserOrm = Depends(get_current_user)):
    """
    Получение информации о текущем пользователе.
    
    Возвращает данные пользователя из базы данных.
    Требует валидный access токен.
    """
    try:
        return SUser.model_validate(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@router.patch(
    "/user-update",
    response_model=SUser,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        400: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def update_user(
    update_data: SUserUpdate,
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновление данных пользователя.
    
    Позволяет обновить био, пол, дату рождения и аватарку.
    Требует валидный access токен.
    Можно не передавать те параметры которые пользователь не обновлял
    """
    try:
        # Проверяем, существует ли файл аватарки, если он указан
        if update_data.avatar_id is not None:
            # Исключительное говно по кодстайлу, но так реальлно проще в данном конкретном случае!
            from database import new_session
            from models.files import FileOrm
            from sqlalchemy import select
            
            async with new_session() as session:
                query = select(FileOrm).where(FileOrm.id == update_data.avatar_id)
                result = await session.execute(query)
                file = result.scalars().first()
                
                if not file:
                    raise HTTPException(
                        status_code=400, 
                        detail="Файл аватарки не найден"
                    )
        
        # Обновляем данные пользователя
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_user = await UserRepository.update_user(current_user.id, update_dict)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return SUser.model_validate(updated_user)
        
    except HTTPException:
        raise
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/users/{user_id}",
    response_model=SPublicUser,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
        500: {"model": ErrorResponse}
    }
)
async def get_user_by_id(
    user_id: int = Path(..., description="ID пользователя"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получение публичной информации о пользователе по ID.
    
    Возвращает публичную информацию о пользователе: username, био, аватарку,
    онлайн статус и время последней активности.
    Требует валидный access токен.
    """
    try:
        if user_id == current_user.id:
            # Если запрашиваем свой профиль, используем полную информацию
            return SUser.model_validate(current_user)
        
        user_info = await UserRepository.get_public_user_info(user_id)
        
        if not user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return SPublicUser.model_validate(user_info)
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/users/{user_id}/status",
    response_model=SUserStatus,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
        500: {"model": ErrorResponse}
    }
)
async def get_user_status(
    user_id: int = Path(..., description="ID пользователя"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получение статуса пользователя по ID.
    
    Возвращает информацию о том, онлайн ли пользователь,
    и когда он был в сети последний раз.
    Требует валидный access токен.
    """
    try:
        user_status = await UserRepository.get_user_status(user_id)
        
        if not user_status:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return SUserStatus.model_validate(user_status)
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )