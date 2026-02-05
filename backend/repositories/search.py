from datetime import datetime
from datetime import timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from database import new_session
from models.auth import UserOrm
from models.chat import MessageOrm, ChatParticipantOrm
from models.files import FileOrm




class UserSearchRepository:
    """Репозиторий для поиска пользователей"""
    
    
    @classmethod
    async def search_users(
        cls, 
        current_user_id: int,
        username_query: str,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Ищет пользователей по username (регистронезависимый поиск)"""
        async with new_session() as session:
            # Ищем пользователей, username которых содержит запрос
            query = select(
                UserOrm.id,
                UserOrm.username,
                UserOrm.avatar_id,
                UserOrm.bio,
                UserOrm.is_online,
                UserOrm.last_seen
            ).where(
                and_(
                    UserOrm.username.ilike(f"%{username_query}%"),
                    UserOrm.id != current_user_id  # Исключаем текущего пользователя
                )
            ).order_by(
                UserOrm.username
            ).offset(skip).limit(limit)
            
            result = await session.execute(query)
            rows = result.all()
            
            users = []
            for row in rows:
                user_data = {
                    "id": row.id,
                    "username": row.username,
                    "avatar_id": row.avatar_id,
                    "bio": row.bio,
                    "is_online": row.is_online,
                    "last_seen": row.last_seen,
                    "avatar_url": await cls._get_user_avatar_url(row.avatar_id)
                }
                users.append(user_data)
            
            return users
    
    
    @classmethod
    async def search_users_exact(
        cls,
        current_user_id: int,
        username_query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Ищет пользователей по точному совпадению username"""
        async with new_session() as session:
            query = select(
                UserOrm.id,
                UserOrm.username,
                UserOrm.avatar_id,
                UserOrm.bio,
                UserOrm.is_online,
                UserOrm.last_seen
            ).where(
                and_(
                    UserOrm.username == username_query,
                    UserOrm.id != current_user_id
                )
            ).order_by(
                UserOrm.username
            ).offset(skip).limit(limit)
            
            result = await session.execute(query)
            rows = result.all()
            
            users = []
            for row in rows:
                user_data = {
                    "id": row.id,
                    "username": row.username,
                    "avatar_id": row.avatar_id,
                    "bio": row.bio,
                    "is_online": row.is_online,
                    "last_seen": row.last_seen,
                    "avatar_url": await cls._get_user_avatar_url(row.avatar_id)
                }
                users.append(user_data)
            
            return users
    
    
    @classmethod
    async def _get_user_avatar_url(cls, avatar_id: Optional[int]) -> Optional[str]:
        """Получает URL аватарки пользователя"""
        if not avatar_id:
            return None
        
        async with new_session() as session:
            file_query = select(FileOrm.filename).where(FileOrm.id == avatar_id)
            file_result = await session.execute(file_query)
            filename = file_result.scalar_one_or_none()
            
            if not filename:
                return None
            
            try:
                from utils.minio_client import minio
                return await minio.get_url(filename)
            except Exception:
                return None




class MessageSearchRepository:
    """Репозиторий для поиска сообщений"""
    
    
    @classmethod
    async def search_messages_global(
        cls,
        current_user_id: int,
        text_query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Ищет текстовые сообщения во всех чатах пользователя"""
        async with new_session() as session:
            # Получаем список чатов, в которых участвует пользователь
            user_chats_query = select(ChatParticipantOrm.chat_id).where(
                ChatParticipantOrm.user_id == current_user_id
            )
            
            # Ищем сообщения в чатах пользователя, которые содержат текст
            query = select(MessageOrm).where(
                and_(
                    MessageOrm.chat_id.in_(user_chats_query),
                    MessageOrm.content.isnot(None),
                    MessageOrm.content.ilike(f"%{text_query}%")
                )
            ).order_by(
                MessageOrm.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            return await cls._messages_to_dicts(messages, session)
    
    
    @classmethod
    async def search_messages_in_chat(
        cls,
        current_user_id: int,
        chat_id: int,
        text_query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Ищет текстовые сообщения в конкретном чате"""
        async with new_session() as session:
            # Проверяем, является ли пользователь участником чата
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == current_user_id
            )
            participant_result = await session.execute(participant_query)
            
            if not participant_result.scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")
            
            # Ищем сообщения в чате, которые содержат текст
            query = select(MessageOrm).where(
                and_(
                    MessageOrm.chat_id == chat_id,
                    MessageOrm.content.isnot(None),
                    MessageOrm.content.ilike(f"%{text_query}%")
                )
            ).order_by(
                MessageOrm.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            return await cls._messages_to_dicts(messages, session)
    
    
    @classmethod
    async def search_messages_by_username(
        cls,
        current_user_id: int,
        username_query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Ищет сообщения от пользователя с указанным username"""
        async with new_session() as session:
            # Находим ID пользователя по username
            user_query = select(UserOrm.id).where(
                UserOrm.username.ilike(f"%{username_query}%")
            )
            user_result = await session.execute(user_query)
            user_ids = [row.id for row in user_result.all()]
            
            if not user_ids:
                return []
            
            # Получаем список чатов, в которых участвует пользователь
            user_chats_query = select(ChatParticipantOrm.chat_id).where(
                ChatParticipantOrm.user_id == current_user_id
            )
            
            # Ищем сообщения от найденных пользователей в чатах текущего пользователя
            query = select(MessageOrm).where(
                and_(
                    MessageOrm.chat_id.in_(user_chats_query),
                    MessageOrm.sender_id.in_(user_ids),
                    MessageOrm.content.isnot(None)
                )
            ).order_by(
                MessageOrm.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            return await cls._messages_to_dicts(messages, session)
    
    
    @classmethod
    async def _messages_to_dicts(
        cls,
        messages: List[MessageOrm],
        session
    ) -> List[Dict[str, Any]]:
        """Конвертирует список объектов MessageOrm в список словарей"""
        from repositories.chat import MessageRepository
        
        messages_dicts = []
        for message in messages:
            # Получаем информацию об отправителе
            sender_query = select(
                UserOrm.username, UserOrm.avatar_id
            ).where(UserOrm.id == message.sender_id)
            
            sender_result = await session.execute(sender_query)
            sender_row = sender_result.first()
            
            sender_username = None
            sender_avatar_url = None
            
            if sender_row:
                sender_username = sender_row.username
                sender_avatar_url = await cls._get_user_avatar_url(sender_row.avatar_id)
            
            # Получаем информацию о файле
            file_url = None
            if message.file_id:
                file_query = select(FileOrm.filename).where(FileOrm.id == message.file_id)
                file_result = await session.execute(file_query)
                filename = file_result.scalar_one_or_none()
                
                if filename:
                    try:
                        from utils.minio_client import minio
                        file_url = await minio.get_url(filename)
                    except Exception:
                        pass
            
            message_dict = {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "sender_username": sender_username,
                "sender_avatar_url": sender_avatar_url,
                "message_type": message.message_type,
                "content": message.content,
                "file_id": message.file_id,
                "file_url": file_url,
                "reply_to_id": message.reply_to_id,
                "status": message.status,
                "edited": message.edited,
                "metadata": message.message_metadata,
                "created_at": message.created_at,
                "updated_at": message.updated_at
            }
            
            messages_dicts.append(message_dict)
        
        return messages_dicts
    
    
    @classmethod
    async def _get_user_avatar_url(cls, avatar_id: Optional[int]) -> Optional[str]:
        """Получает URL аватарки пользователя"""
        if not avatar_id:
            return None
        
        async with new_session() as session:
            file_query = select(FileOrm.filename).where(FileOrm.id == avatar_id)
            file_result = await session.execute(file_query)
            filename = file_result.scalar_one_or_none()
            
            if not filename:
                return None
            
            try:
                from utils.minio_client import minio
                return await minio.get_url(filename)
            except Exception:
                return None