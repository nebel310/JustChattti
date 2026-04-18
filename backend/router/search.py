from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body

from models.auth import UserOrm
from repositories.search import UserSearchRepository, MessageSearchRepository
from schemas.search import (
    UserSearchRequest, UserSearchResponse,
    MessageSearchRequest, MessageSearchResponse
)
from schemas.base import ErrorResponse, ValidationErrorResponse
from utils.security import get_current_user




router = APIRouter(
    prefix="/search",
    tags=["Поиск"]
)


@router.post(
    "/users",
    response_model=UserSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_users(
    search_request: UserSearchRequest,
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск пользователей по username.
    
    Возвращает список пользователей, чей username содержит указанную строку.
    Регистронезависимый поиск.
    """
    try:
        if len(search_request.username) < 1:
            raise HTTPException(
                status_code=400,
                detail="Запрос для поиска не может быть пустым"
            )
        
        users = await UserSearchRepository.search_users(
            current_user.id,
            search_request.username,
            skip,
            limit
        )
        
        # Для простоты считаем, что всего результатов примерно столько же
        # В реальном приложении нужно делать отдельный запрос COUNT
        total_estimate = len(users) + skip
        
        return UserSearchResponse(
            users=users,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(users) == limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users/username/{username}",
    response_model=UserSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_users_by_exact_username(
    username: str = Path(..., description="Точный username для поиска"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск пользователей по точному совпадению username.
    
    Возвращает список пользователей с указанным username.
    """
    try:
        if len(username) < 1:
            raise HTTPException(
                status_code=400,
                detail="Username для поиска не может быть пустым"
            )
        
        users = await UserSearchRepository.search_users_exact(
            current_user.id,
            username,
            skip,
            limit
        )
        
        total_estimate = len(users) + skip
        
        return UserSearchResponse(
            users=users,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(users) == limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/messages/global",
    response_model=MessageSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_messages_global(
    search_request: MessageSearchRequest,
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    cursor: Optional[str] = Query(None, description="Курсор для пагинации"),
    direction: str = Query("before", regex="^(before|after)$", description="Направление пагинации"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Глобальный полнотекстовый поиск по сообщениям с keyset-пагинацией.
    """
    try:
        if len(search_request.text) < 1:
            raise HTTPException(status_code=400, detail="Текст для поиска не может быть пустым")
        
        result = await MessageSearchRepository.search_messages_global(
            current_user_id=current_user.id,
            text_query=search_request.text,
            limit=limit,
            cursor=cursor,
            direction=direction
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/messages/chat/{chat_id}",
    response_model=MessageSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        403: {"model": ErrorResponse, "description": "Нет доступа к чату"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_messages_in_chat(
    chat_id: int = Path(..., description="ID чата для поиска"),
    search_request: MessageSearchRequest = Body(...),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    cursor: Optional[str] = Query(None, description="Курсор для пагинации"),
    direction: str = Query("before", regex="^(before|after)$", description="Направление пагинации"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Полнотекстовый поиск по сообщениям в конкретном чате с keyset-пагинацией.
    """
    try:
        if len(search_request.text) < 1:
            raise HTTPException(status_code=400, detail="Текст для поиска не может быть пустым")
        
        result = await MessageSearchRepository.search_messages_in_chat(
            current_user_id=current_user.id,
            chat_id=chat_id,
            text_query=search_request.text,
            limit=limit,
            cursor=cursor,
            direction=direction
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/messages/username/{username}",
    response_model=MessageSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_messages_by_username(
    username: str = Path(..., description="Username отправителя для поиска"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    cursor: Optional[str] = Query(None, description="Курсор для пагинации"),
    direction: str = Query("before", regex="^(before|after)$", description="Направление пагинации"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск сообщений от пользователей с указанным username (keyset-пагинация).
    """
    try:
        if len(username) < 1:
            raise HTTPException(status_code=400, detail="Username для поиска не может быть пустым")
        
        result = await MessageSearchRepository.search_messages_by_username(
            current_user_id=current_user.id,
            username_query=username,
            limit=limit,
            cursor=cursor,
            direction=direction
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get(
    "/messages/sender/{user_id}",
    response_model=MessageSearchResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации запроса"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def search_messages_by_user_id(
    user_id: int = Path(..., description="ID отправителя для поиска"),
    text_query: Optional[str] = Query(
        None,
        description="Текст для поиска в сообщениях (опционально)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    cursor: Optional[str] = Query(None, description="Курсор для пагинации"),
    direction: str = Query("before", regex="^(before|after)$", description="Направление пагинации"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск сообщений от пользователя по его ID с keyset-пагинацией.
    Если указан text_query, ищет только сообщения, содержащие этот текст.
    Поиск только во всех чатах текущего пользователя.
    """
    try:
        result = await MessageSearchRepository.search_messages_by_sender(
            current_user_id=current_user.id,
            sender_id=user_id,
            text_query=text_query,
            limit=limit,
            cursor=cursor,
            direction=direction
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))