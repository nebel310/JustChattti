from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile, File, Path

from repositories.files import FileRepository
from schemas.files import (
    SUploadFile, SUploadFileResponse, ErrorResponse, SFileResponse
)
from models.auth import UserOrm
from utils.security import get_current_user




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