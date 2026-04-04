from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile, File, Path
from fastapi.responses import StreamingResponse

from repositories.files import FileRepository
from schemas.files import (
    SUploadFile, SUploadFileResponse, SFileResponse
)
from schemas.base import ErrorResponse
from models.auth import UserOrm
from utils.security import get_current_user
from utils.minio_client import minio




router = APIRouter(
    prefix="/files",
    tags=["Файлы"]
)


@router.post(
    "/upload",
    response_model=SUploadFileResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации файла"},
        500: {"model": ErrorResponse}
    }
)
async def upload_file(
    file_data: SUploadFile,
    file: UploadFile = File(...),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Загрузка файла на сервер.
    
    Поддерживаются изображения, видео, аудио и документы.
    Можно указать тип файла (аватарка, голосовое сообщение).
    """
    try:
        answer = await FileRepository.upload_file(file, file_data, current_user.id)
        return SUploadFileResponse(
            success=True,
            file_id=answer["id"],
            filename=answer["filename"],
            original_name=answer["original_name"],
            filetype=answer["filetype"],
            filesubtype=answer["filesubtype"],
            uploaded_by_id=answer["uploaded_by_id"],
            created_at=answer["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{file_id}",
    response_model=SFileResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Файл не найден"},
        500: {"model": ErrorResponse}
    }
)
async def get_file(
    file_id: int = Path(..., description="ID файла"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Получение информации о файле и ссылки для скачивания.
    
    Возвращает метаданные файла и временную ссылку (действует 1 час).
    """
    try:
        file_info = await FileRepository.get_file_by_id(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return SFileResponse(**file_info)
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{file_id}/download",
    responses={
        200: {
            "description": "Файл для скачивания",
            "content": {
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        403: {"model": ErrorResponse, "description": "Нет доступа к файлу"},
        404: {"model": ErrorResponse, "description": "Файл не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def download_file(
    file_id: int = Path(..., description="ID файла"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Скачивание файла напрямую через сервер.
    
    Возвращает файл как поток для скачивания с оригинальным именем.
    Проверяет права доступа к файлу.
    """
    try:
        # Получаем информацию о файле
        file_info = await FileRepository.get_file_by_id(file_id, current_user.id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        # Проверяем права доступа
        if file_info["uploaded_by_id"] != current_user.id:
            # Проверяем, есть ли доступ через сообщения в общих чатах
            from database import new_session
            from sqlalchemy import select
            from models.chat import MessageOrm
            
            async with new_session() as session:
                # Ищем сообщения с этим файлом в чатах, где пользователь участник
                query = select(MessageOrm.id).join(
                    MessageOrm.chat
                ).where(
                    MessageOrm.file_id == file_id
                ).exists()
                
                # Получаем список чатов пользователя
                from models.chat import ChatParticipantOrm
                user_chats_query = select(ChatParticipantOrm.chat_id).where(
                    ChatParticipantOrm.user_id == current_user.id
                )
                
                # Ищем сообщения в чатах пользователя с этим файлом
                from sqlalchemy import and_
                message_query = select(MessageOrm.id).where(
                    and_(
                        MessageOrm.file_id == file_id,
                        MessageOrm.chat_id.in_(user_chats_query)
                    )
                )
                
                message_result = await session.execute(message_query)
                if not message_result.first():
                    raise HTTPException(
                        status_code=403, 
                        detail="Нет доступа к файлу"
                    )
        
        # Получаем файл из MinIO
        filename = file_info["filename"]
        
        async def file_stream():
            """Генератор для потоковой передачи файла"""
            async with minio.session.client(
                's3',
                endpoint_url=minio.endpoint,
                aws_access_key_id=minio.minio_access_key,
                aws_secret_access_key=minio.minio_secret_key,
                region_name='us-east-1'
            ) as client:
                response = await client.get_object(
                    Bucket=minio.bucket,
                    Key=filename
                )
                
                async for chunk in response['Body'].iter_chunks():
                    yield chunk
        
        # Определяем Content-Type
        content_type = "application/octet-stream"
        if file_info["filetype"] == "image":
            ext = filename.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg']:
                content_type = "image/jpeg"
            elif ext == 'png':
                content_type = "image/png"
            elif ext == 'gif':
                content_type = "image/gif"
            elif ext == 'webp':
                content_type = "image/webp"
        elif file_info["filetype"] == "video":
            content_type = "video/mp4"
        elif file_info["filetype"] == "audio":
            content_type = "audio/mpeg"
        
        # Возвращаем файл как поток
        return StreamingResponse(
            file_stream(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{file_info['original_name']}\"",
                "Content-Length": str(file_info.get("size", 0))
            }
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{file_id}",
    responses={
        200: {"description": "Файл успешно удален"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Файл не найден"},
        500: {"model": ErrorResponse}
    }
)
async def delete_file(
    file_id: int = Path(..., description="ID файла"),
    current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаление файла.
    
    Удаляет файл из MinIO и базы данных.
    Если файл используется как аватарка, аватарка будет сброшена.
    """
    try:
        deleted = await FileRepository.delete_file(file_id, current_user.id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Файл не найден или у вас нет прав на его удаление")
        
        return {"message": "Файл успешно удален"}
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))