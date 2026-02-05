import os
import uuid
from typing import Dict, Any

from sqlalchemy import delete, select

from database import new_session
from models.files import FileOrm
from schemas.files import SUploadFile
from utils.minio_client import minio




class FileRepository:
    """Репозиторий для работы с файлами"""
    @classmethod
    async def _determine_filetype(cls, file):
        """Метод для определения filetype"""
        if file.content_type.startswith('image/'): return 'image'
        if file.content_type.startswith('video/'): return 'video'
        if file.content_type.startswith('audio/'): return 'audio'
        return 'other'
    
    @classmethod
    async def _determine_filesubtype(cls, file_data: SUploadFile):
        """Метод для определения filesubtype"""
        if file_data.is_avatar: return 'avatar'
        if file_data.is_voice_message: return 'voice_message'
        return 'other'
    
    @classmethod
    async def upload_file(cls, file, file_data: SUploadFile, user_id: int) -> Dict[str, Any]:
        """Метод для загрузки файл на сервер"""
        async with new_session() as session:            
            filename_in_minio = await minio.upload(file)
            
            filetype = await cls._determine_filetype(file)
            filesubtype = await cls._determine_filesubtype(file_data)
            
            file_orm = FileOrm(
                filename=filename_in_minio,
                original_name=file.filename,
                filetype=filetype,
                filesubtype=filesubtype,
                uploaded_by_id=user_id
            )
            
            session.add(file_orm)
            await session.flush()
            await session.commit()
            
            return {
                "id": file_orm.id,
                "filename": file_orm.filename,
                "original_name": file_orm.original_name,
                "filetype": file_orm.filetype,
                "filesubtype": file_orm.filesubtype,
                "uploaded_by_id": file_orm.uploaded_by_id,
                "created_at": file_orm.created_at
            }
    
    @classmethod
    async def get_file_by_id(cls, file_id: int, user_id: int = None) -> Dict[str, Any] | None:
        """Получение информации о файле по ID."""
        async with new_session() as session:
            query = select(FileOrm).where(FileOrm.id == file_id)
            if user_id:
                query = query.where(FileOrm.uploaded_by_id == user_id)
            
            result = await session.execute(query)
            file = result.scalars().first()
            
            if not file:
                return None
            
            # Генерируем временную ссылку на файл
            try:
                file_url = await minio.get_url(file.filename)
            except Exception:
                file_url = None
            
            return {
                "id": file.id,
                "filename": file.filename,
                "original_name": file.original_name,
                "filetype": file.filetype,
                "filesubtype": file.filesubtype,
                "uploaded_by_id": file.uploaded_by_id,
                "created_at": file.created_at,
                "url": file_url
            }
    
    @classmethod
    async def delete_file(cls, file_id: int, user_id: int) -> bool:
        """Удаление файла по ID."""
        async with new_session() as session:
            # Получаем файл
            query = select(FileOrm).where(
                FileOrm.id == file_id,
                FileOrm.uploaded_by_id == user_id
            )
            result = await session.execute(query)
            file = result.scalars().first()
            
            if not file:
                return False
            
            # Проверяем, используется ли файл как аватарка
            from models.auth import UserOrm
            user_query = select(UserOrm).where(UserOrm.avatar_id == file_id)
            user_result = await session.execute(user_query)
            users_with_avatar = user_result.scalars().all()
            
            # Обнуляем аватарку у всех пользователей, если файл используется как аватарка
            for user in users_with_avatar:
                user.avatar_id = None
            
            # Удаляем файл из MinIO
            try:
                await minio.delete(file.filename)
            except Exception as e:
                print(f"Ошибка при удалении файла из MinIO: {e}")
            
            # Удаляем запись из базы
            await session.delete(file)
            await session.commit()
            
            return True