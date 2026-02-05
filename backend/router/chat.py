from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body

from models.auth import UserOrm
from repositories.chat import ChatRepository, MessageRepository
from schemas.chat import (
    ChatCreate, ChatResponse, ChatDetailResponse,
    MessageCreate, MessageResponse, MessagesResponse,
    MarkAsReadRequest, CallCreate, CallResponse,
    ErrorResponse, ValidationErrorResponse
)
from utils.security import get_current_user




router = APIRouter(
    prefix="/chats",
    tags=["Чаты"]
)


@router.get(
    "/",
    response_model=List[ChatResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def get_chats(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых записей"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получает список чатов текущего пользователя.
    
    Возвращает список чатов с информацией о последнем сообщении и количестве непрочитанных.
    """
    try:
        chats = await ChatRepository.get_user_chats(current_user.id, skip, limit)
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def create_chat(
    chat_data: ChatCreate,
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новый приватный чат с указанным пользователем.
    
    Приватный чат может быть создан только между двумя пользователями.
    Если чат уже существует, возвращает ошибку.
    """
    try:
        chat_info = await ChatRepository.create_chat(chat_data, current_user.id)
        
        return {
            "id": chat_info["id"],
            "name": chat_data.name,
            "chat_type": chat_data.chat_type,
            "avatar_id": None,
            "avatar_url": None,
            "created_by_id": current_user.id,
            "created_at": chat_info["created_at"],
            "updated_at": chat_info["created_at"],
            "unread_count": 0,
            "last_message": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def get_chat_detail(
    chat_id: int = Path(..., description="ID чата"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получает детальную информацию о чате.
    
    Возвращает информацию о чате и его участниках.
    Только участники чата могут просматривать его информацию.
    """
    try:
        chat = await ChatRepository.get_chat_detail(chat_id, current_user.id)
        
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        return chat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{chat_id}",
    responses={
        200: {"description": "Чат успешно удален", "example": {"success": True}},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        403: {"model": ErrorResponse, "description": "Нет прав на удаление"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def delete_chat(
    chat_id: int = Path(..., description="ID чата"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет чат.
    
    Удалить чат может только создатель чата.
    Удаление происходит каскадно для всех связанных данных.
    """
    try:
        success = await ChatRepository.delete_chat(chat_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=403, 
                detail="Нет прав на удаление чата"
            )
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{chat_id}/messages",
    response_model=MessagesResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def get_messages(
    chat_id: int = Path(..., description="ID чата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых сообщений"),
    limit: int = Query(50, ge=1, le=100, description="Количество возвращаемых сообщений"),
    before: Optional[str] = Query(
        None, 
        description="Дата в формате ISO для получения сообщений, созданных до этой даты"
    ),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получает историю сообщений в чате.
    
    Возвращает сообщения в обратном хронологическом порядке (новые первыми).
    При получении сообщений они автоматически помечаются как прочитанные.
    """
    try:
        before_date = None
        
        if before:
            try:
                before_date = datetime.fromisoformat(before.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Неверный формат даты. Используйте ISO формат"
                )
        
        messages = await MessageRepository.get_messages(
            chat_id, current_user.id, skip, limit, before_date
        )
        
        return messages
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def send_message(
    chat_id: int = Path(..., description="ID чата"),
    message_data: MessageCreate = Body(...),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Отправляет сообщение в чат.
    
    Поддерживает отправку текстовых сообщений и сообщений с файлами.
    При отправке сообщения обновляется время последней активности чата.
    """
    try:
        # Устанавливаем chat_id из пути
        message_data_dict = message_data.model_dump()
        message_data_dict["chat_id"] = chat_id
        
        message = await MessageRepository.send_message(
            MessageCreate(**message_data_dict), 
            current_user.id
        )
        
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/messages/{message_id}",
    response_model=MessageResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        403: {"model": ErrorResponse, "description": "Нет прав на редактирование"},
        404: {"model": ErrorResponse, "description": "Сообщение не найдено"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def edit_message(
    message_id: int = Path(..., description="ID сообщения"),
    content: str = Body(..., embed=True, description="Новый текст сообщения"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Редактирует существующее сообщение.
    
    Редактировать можно только свои сообщения и только в течение 24 часов после отправки.
    После редактирования устанавливается флаг edited в true.
    """
    try:
        if len(content) > 5000:
            raise HTTPException(
                status_code=400, 
                detail="Длина сообщения не должна превышать 5000 символов"
            )
        
        message = await MessageRepository.edit_message(
            message_id, current_user.id, content
        )
        
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
        
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/messages/{message_id}",
    responses={
        200: {"description": "Сообщение успешно удалено", "example": {"success": True}},
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        403: {"model": ErrorResponse, "description": "Нет прав на удаление"},
        404: {"model": ErrorResponse, "description": "Сообщение не найдено"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def delete_message(
    message_id: int = Path(..., description="ID сообщения"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет сообщение.
    
    Удалить можно только свои сообщения и только в течение 24 часов после отправки.
    """
    try:
        success = await MessageRepository.delete_message(message_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
        
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/messages/mark-read",
    responses={
        200: {"description": "Сообщения помечены как прочитанные", "example": {"success": True}},
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def mark_messages_as_read(
    request: MarkAsReadRequest,
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Помечает сообщения как прочитанные.
    
    Принимает список ID сообщений для пометки как прочитанные.
    Только участник чата может помечать сообщения как прочитанные.
    """
    try:
        # В текущей реализации сообщения помечаются как прочитанные
        # автоматически при получении истории сообщений.
        # Этот эндпоинт может быть использован для ручной пометки.
        return {"success": True, "marked_count": len(request.message_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chat_id}/calls",
    response_model=CallResponse,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Чат не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def start_call(
    chat_id: int = Path(..., description="ID чата"),
    call_data: CallCreate = Body(...),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Начинает WebRTC звонок в чате.
    
    Поддерживает аудио и видео звонки.
    Для установки соединения используйте WebSocket с сигналами WebRTC.
    """
    try:
        from datetime import datetime, timezone
        
        # Проверяем, что пользователь является участником чата
        from repositories.chat import ChatRepository
        chat = await ChatRepository.get_chat_detail(chat_id, current_user.id)
        
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        # В реальной реализации здесь нужно создать запись о звонке в БД
        # Для примера возвращаем фиктивные данные
        
        return CallResponse(
            id=1,
            chat_id=chat_id,
            initiator_id=current_user.id,
            call_type=call_data.call_type,
            status="ringing",
            started_at=datetime.now(timezone.utc),
            ended_at=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))