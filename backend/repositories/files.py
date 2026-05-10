from typing import Dict, Any

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database import new_session
from models.files import FileOrm
from models.auth import UserOrm
from models.chat import MessageOrm
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
        """Метод для загрузки файла на сервер с проверкой лимита хранилища"""
        async with new_session() as session:
            # Получаем пользователя и проверяем лимит
            user = await session.get(UserOrm, user_id)
            if not user:
                raise ValueError("Пользователь не найден")
            
            # Получаем размер файла
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            # Проверяем, не превысит ли новый файл лимит
            if user.storage_used_bytes + file_size > user.storage_limit_bytes:
                raise ValueError(
                    f"Недостаточно места в хранилище. "
                    f"Использовано: {user.storage_used_bytes}, "
                    f"лимит: {user.storage_limit_bytes}, "
                    f"размер файла: {file_size}"
                )
            
            # Загружаем файл в MinIO
            filename_in_minio = await minio.upload(file)
            
            filetype = await cls._determine_filetype(file)
            filesubtype = await cls._determine_filesubtype(file_data)
            
            file_orm = FileOrm(
                filename=filename_in_minio,
                original_name=file.filename,
                filetype=filetype,
                filesubtype=filesubtype,
                size=file_size,
                uploaded_by_id=user_id
            )
            
            session.add(file_orm)
            
            # Обновляем used_bytes пользователя
            user.storage_used_bytes += file_size
            
            try:
                await session.flush()
                await session.commit()
            except SQLAlchemyError as e:
                # Если произошла ошибка БД, пробуем удалить файл из MinIO
                try:
                    await minio.delete(filename_in_minio)
                except Exception:
                    pass
                raise ValueError(f"Ошибка базы данных: {str(e)}") from e
            
            return {
                "id": file_orm.id,
                "filename": file_orm.filename,
                "original_name": file_orm.original_name,
                "filetype": file_orm.filetype,
                "filesubtype": file_orm.filesubtype,
                "size": file_orm.size,          # <-- добавлено
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
                "size": file.size,              # <-- добавлено
                "uploaded_by_id": file.uploaded_by_id,
                "created_at": file.created_at,
                "url": file_url
            }
    
    @classmethod
    async def delete_file(cls, file_id: int, user_id: int) -> bool:
        """Удаление файла по ID с уменьшением использованного места пользователя"""
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
            
            # Получаем пользователя для обновления used_bytes
            user = await session.get(UserOrm, user_id)
            if not user:
                return False
            
            file_size = file.size
            
            # Проверяем, используется ли файл как аватарка
            user_query = select(UserOrm).where(UserOrm.avatar_id == file_id)
            user_result = await session.execute(user_query)
            users_with_avatar = user_result.scalars().all()
            
            # Обнуляем аватарку у всех пользователей, если файл используется как аватарка
            for u in users_with_avatar:
                u.avatar_id = None
            
            # Удаляем файл из MinIO
            try:
                await minio.delete(file.filename)
            except Exception as e:
                print(f"Ошибка при удалении файла из MinIO: {e}")
            
            # Удаляем запись из базы
            await session.delete(file)
            
            # Уменьшаем used_bytes пользователя
            user.storage_used_bytes -= file_size
            if user.storage_used_bytes < 0:
                user.storage_used_bytes = 0
            
            await session.commit()
            
            return True
    
    
    @classmethod
    async def get_storage_usage(cls, user_id: int) -> dict:
        async with new_session() as session:
            stmt = select(
                FileOrm.filetype,
                FileOrm.filesubtype,
                func.sum(FileOrm.size).label('total_size'),
                func.count(FileOrm.id).label('cnt')
            ).join(
                MessageOrm, FileOrm.id == MessageOrm.file_id
            ).where(
                MessageOrm.sender_id == user_id,
                MessageOrm.file_id.is_not(None)
            ).group_by(FileOrm.filetype, FileOrm.filesubtype)

            rows = (await session.execute(stmt)).all()

            user_stmt = select(UserOrm.storage_used_bytes, UserOrm.storage_limit_bytes).where(UserOrm.id == user_id)
            user_row = (await session.execute(user_stmt)).first()
            total_used = user_row.storage_used_bytes if user_row else 0
            limit = user_row.storage_limit_bytes if user_row else 0

            by_type = {}
            for filetype, filesubtype, total_size, cnt in rows:
                category = filetype
                if filetype == "audio" and filesubtype == "voice_message":
                    category = "voice"
                elif filetype == "audio":
                    category = "audio"
                if category not in by_type:
                    by_type[category] = {"total_bytes": 0, "file_count": 0}
                by_type[category]["total_bytes"] += total_size or 0
                by_type[category]["file_count"] += cnt or 0

            by_type_list = [
                {"file_type": k, "total_bytes": v["total_bytes"], "file_count": v["file_count"]}
                for k, v in by_type.items()
            ]

            return {
                "total_used_bytes": total_used,
                "limit_bytes": limit,
                "by_type": by_type_list
            }