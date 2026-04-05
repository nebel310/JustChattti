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
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Глобальный поиск по сообщениям.
    
    Ищет текстовые сообщения во всех чатах текущего пользователя.
    Возвращает сообщения, содержащие указанный текст.
    Регистронезависимый поиск.
    """
    try:
        if len(search_request.text) < 1:
            raise HTTPException(
                status_code=400,
                detail="Текст для поиска не может быть пустым"
            )
        
        messages = await MessageSearchRepository.search_messages_global(
            current_user.id,
            search_request.text,
            skip,
            limit
        )
        
        total_estimate = len(messages) + skip
        
        return MessageSearchResponse(
            messages=messages,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(messages) == limit
        )
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
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск по сообщениям в конкретном чате.
    
    Ищет текстовые сообщения в указанном чате.
    Возвращает сообщения, содержащие указанный текст.
    Регистронезависимый поиск.
    Только участники чата могут искать сообщения в нем.
    """
    try:
        if len(search_request.text) < 1:
            raise HTTPException(
                status_code=400,
                detail="Текст для поиска не может быть пустым"
            )
        
        messages = await MessageSearchRepository.search_messages_in_chat(
            current_user.id,
            chat_id,
            search_request.text,
            skip,
            limit
        )
        
        total_estimate = len(messages) + skip
        
        return MessageSearchResponse(
            messages=messages,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(messages) == limit
        )
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
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск сообщений от указанного пользователя.
    
    Ищет сообщения от пользователей, чей username содержит указанную строку.
    Поиск только по текстовым сообщениям во всех чатах текущего пользователя.
    Регистронезависимый поиск по username.
    """
    try:
        if len(username) < 1:
            raise HTTPException(
                status_code=400,
                detail="Username для поиска не может быть пустым"
            )
        
        messages = await MessageSearchRepository.search_messages_by_username(
            current_user.id,
            username,
            skip,
            limit
        )
        
        total_estimate = len(messages) + skip
        
        return MessageSearchResponse(
            messages=messages,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(messages) == limit
        )
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
    skip: int = Query(0, ge=0, description="Количество пропускаемых результатов"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых результатов"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Поиск сообщений от пользователя по его ID.
    
    Ищет сообщения от указанного пользователя.
    Если указан text_query, ищет только сообщения, содержащие этот текст.
    Поиск только во всех чатах текущего пользователя.
    """
    try:
        # Используем существующий метод поиска по username, но сначала находим username по ID
        from repositories.auth import UserRepository
        
        user_info = await UserRepository.get_public_user_info(user_id)
        if not user_info:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        
        # Если указан text_query, используем комбинированный поиск
        if text_query:
            # Получаем все сообщения от пользователя
            all_messages = await MessageSearchRepository.search_messages_by_username(
                current_user.id,
                user_info["username"],
                0,
                1000  # Большой лимит для фильтрации на стороне Python
            )
            
            # Фильтруем по тексту
            filtered_messages = [
                msg for msg in all_messages
                if msg["content"] and text_query.lower() in msg["content"].lower()
            ]
            
            # Применяем пагинацию
            start_idx = skip
            end_idx = skip + limit
            paginated_messages = filtered_messages[start_idx:end_idx]
            
            total_estimate = len(filtered_messages)
        else:
            # Просто ищем все сообщения от пользователя
            messages = await MessageSearchRepository.search_messages_by_username(
                current_user.id,
                user_info["username"],
                skip,
                limit
            )
            
            paginated_messages = messages
            total_estimate = len(messages) + skip
        
        return MessageSearchResponse(
            messages=paginated_messages,
            total=total_estimate,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(paginated_messages) == limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))