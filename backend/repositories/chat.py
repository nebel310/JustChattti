from datetime import datetime
from datetime import timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, delete, desc, func, and_, or_
from sqlalchemy.orm import selectinload

from database import new_session
from models.chat import (
    ChatOrm, ChatParticipantOrm, MessageOrm,
    ChatType, MessageStatus, MessageType,
    CallOrm, CallParticipantOrm
)
from models.auth import UserOrm
from models.files import FileOrm
from schemas.chat import ChatCreate, MessageCreate
from utils.minio_client import minio




class ChatRepository:
    """Репозиторий для работы с чатами"""
    @classmethod
    async def create_chat(
        cls, 
        chat_data: ChatCreate, 
        creator_id: int
    ) -> Dict[str, Any]:
        """Создает новый приватный чат между двумя пользователями"""
        async with new_session() as session:
            if len(chat_data.participant_ids) != 1:
                raise ValueError("Приватный чат должен иметь ровно одного участника")
            
            participant_id = chat_data.participant_ids[0]
            
            if participant_id == creator_id:
                raise ValueError("Нельзя создать чат с самим собой")
            
            # Проверяем существование участника
            user_query = select(UserOrm.id).where(UserOrm.id == participant_id)
            user_result = await session.execute(user_query)
            if not user_result.scalar_one_or_none():
                raise ValueError("Участник не найден")
            
            # Проверяем, существует ли уже чат между этими пользователями
            existing_chat_query = select(ChatOrm.id).join(
                ChatParticipantOrm, ChatOrm.id == ChatParticipantOrm.chat_id
            ).where(
                ChatOrm.chat_type == ChatType.PRIVATE,
                ChatParticipantOrm.user_id.in_([creator_id, participant_id])
            ).group_by(ChatOrm.id).having(func.count(ChatParticipantOrm.user_id) == 2)
            
            existing_chat_result = await session.execute(existing_chat_query)
            existing_chat = existing_chat_result.scalar_one_or_none()
            
            if existing_chat:
                raise ValueError("Чат между этими пользователями уже существует")
            
            # Создаем чат
            chat = ChatOrm(
                name=chat_data.name,
                chat_type=ChatType.PRIVATE,
                created_by_id=creator_id
            )
            
            session.add(chat)
            await session.flush()
            
            # Добавляем участников
            participants = [
                ChatParticipantOrm(chat_id=chat.id, user_id=creator_id),
                ChatParticipantOrm(chat_id=chat.id, user_id=participant_id)
            ]
            
            session.add_all(participants)
            await session.commit()
            
            return {"id": chat.id, "created_at": chat.created_at}
    
    
    @classmethod
    async def get_user_chats(
        cls, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получает список чатов пользователя с последним сообщением"""
        async with new_session() as session:
            # Подзапрос для последнего сообщения в чате
            last_message_subquery = select(
                MessageOrm.chat_id,
                func.max(MessageOrm.created_at).label('max_created_at')
            ).group_by(MessageOrm.chat_id).subquery()
            
            # Запрос для получения чатов пользователя
            chats_query = select(ChatOrm).join(
                ChatParticipantOrm, ChatOrm.id == ChatParticipantOrm.chat_id
            ).where(
                ChatParticipantOrm.user_id == user_id
            ).order_by(
                desc(ChatOrm.updated_at)
            ).offset(skip).limit(limit)
            
            chats_result = await session.execute(chats_query)
            chats = chats_result.scalars().all()
            
            chats_list = []
            for chat in chats:
                # Получаем информацию о собеседнике для приватного чата
                participant_query = select(ChatParticipantOrm.user_id).where(
                    ChatParticipantOrm.chat_id == chat.id,
                    ChatParticipantOrm.user_id != user_id
                )
                participant_result = await session.execute(participant_query)
                participant_id = participant_result.scalar_one_or_none()
                
                # Получаем информацию о пользователе-собеседнике
                user_info = {}
                if participant_id:
                    user_query = select(
                        UserOrm.id, UserOrm.username, UserOrm.avatar_id,
                        UserOrm.user_metadata
                    ).where(UserOrm.id == participant_id)
                    user_result = await session.execute(user_query)
                    user_row = user_result.first()
                    
                    if user_row:
                        user_info = {
                            "id": user_row.id,
                            "username": user_row.username,
                            "avatar_id": user_row.avatar_id,
                            "user_metadata": user_row.user_metadata,
                            "avatar_url": await cls._get_user_avatar_url(user_row.avatar_id)
                        }
                
                # Получаем последнее сообщение
                last_message_query = select(MessageOrm).where(
                    MessageOrm.chat_id == chat.id
                ).order_by(desc(MessageOrm.created_at)).limit(1)
                
                last_message_result = await session.execute(last_message_query)
                last_message = last_message_result.scalar_one_or_none()
                
                # Считаем непрочитанные сообщения
                unread_count_query = select(func.count(MessageOrm.id)).where(
                    MessageOrm.chat_id == chat.id,
                    MessageOrm.sender_id != user_id,
                    MessageOrm.status == MessageStatus.SENT
                )
                
                unread_count_result = await session.execute(unread_count_query)
                unread_count = unread_count_result.scalar() or 0
                
                chat_data = {
                    "id": chat.id,
                    "name": chat.name,
                    "chat_type": chat.chat_type,
                    "avatar_id": chat.avatar_id,
                    "avatar_url": await cls._get_avatar_url(chat.avatar_id),
                    "created_by_id": chat.created_by_id,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                    "unread_count": unread_count,
                    "participant_info": user_info,
                    "last_message": None
                }
                
                if last_message:
                    sender_query = select(UserOrm.username).where(
                        UserOrm.id == last_message.sender_id
                    )
                    sender_result = await session.execute(sender_query)
                    sender_username = sender_result.scalar_one_or_none()
                    
                    chat_data["last_message"] = {
                        "id": last_message.id,
                        "content": last_message.content[:100] if last_message.content else None,
                        "message_type": last_message.message_type,
                        "sender_id": last_message.sender_id,
                        "sender_username": sender_username,
                        "created_at": last_message.created_at
                    }
                
                chats_list.append(chat_data)
            
            return chats_list
    
    
    @classmethod
    async def _get_avatar_url(cls, avatar_id: Optional[int]) -> Optional[str]:
        """Получает URL аватарки чата"""
        if not avatar_id:
            return None
        
        async with new_session() as session:
            file_query = select(FileOrm.filename).where(FileOrm.id == avatar_id)
            file_result = await session.execute(file_query)
            filename = file_result.scalar_one_or_none()
            
            if not filename:
                return None
            
            try:
                return await minio.get_url(filename)
            except Exception:
                return None
    
    
    @classmethod
    async def _get_user_avatar_url(cls, avatar_id: Optional[int]) -> Optional[str]:
        """Получает URL аватарки пользователя"""
        return await cls._get_avatar_url(avatar_id)
    
    
    @classmethod
    async def get_chat_detail(
        cls, 
        chat_id: int, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Получает детальную информацию о чате"""
        async with new_session() as session:
            # Проверяем, является ли пользователь участником чата
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == user_id
            )
            participant_result = await session.execute(participant_query)
            if not participant_result.scalar_one_or_none():
                return None
            
            # Получаем информацию о чате
            chat_query = select(ChatOrm).where(ChatOrm.id == chat_id)
            chat_result = await session.execute(chat_query)
            chat = chat_result.scalar_one_or_none()
            
            if not chat:
                return None
            
            # Получаем участников чата
            participants_query = select(
                ChatParticipantOrm.user_id,
                ChatParticipantOrm.joined_at,
                ChatParticipantOrm.last_read_at
            ).where(ChatParticipantOrm.chat_id == chat_id)
            
            participants_result = await session.execute(participants_query)
            participants_rows = participants_result.all()
            
            # Получаем информацию о пользователях-участниках
            participants = []
            for participant_row in participants_rows:
                user_query = select(
                    UserOrm.id, UserOrm.username, UserOrm.avatar_id,
                    UserOrm.user_metadata
                ).where(UserOrm.id == participant_row.user_id)
                
                user_result = await session.execute(user_query)
                user_row = user_result.first()
                
                if user_row:
                    participants.append({
                        "user_id": user_row.id,
                        "username": user_row.username,
                        "avatar_id": user_row.avatar_id,
                        "user_metadata": user_row.user_metadata,
                        "avatar_url": await cls._get_user_avatar_url(user_row.avatar_id),
                        "joined_at": participant_row.joined_at,
                        "last_read_at": participant_row.last_read_at
                    })
            
            # Получаем информацию о собеседнике для приватного чата
            other_participant = None
            for participant in participants:
                if participant["user_id"] != user_id:
                    other_participant = participant
                    break
            
            return {
                "id": chat.id,
                "name": chat.name,
                "chat_type": chat.chat_type,
                "avatar_id": chat.avatar_id,
                "avatar_url": await cls._get_avatar_url(chat.avatar_id),
                "created_by_id": chat.created_by_id,
                "created_at": chat.created_at,
                "updated_at": chat.updated_at,
                "participants": participants,
                "other_participant": other_participant
            }
    
    
    @classmethod
    async def delete_chat(cls, chat_id: int, user_id: int) -> bool:
        """Удаляет чат (только для создателя чата)"""
        async with new_session() as session:
            # Проверяем, является ли пользователь создателем чата
            chat_query = select(ChatOrm).where(
                ChatOrm.id == chat_id,
                ChatOrm.created_by_id == user_id
            )
            chat_result = await session.execute(chat_query)
            chat = chat_result.scalar_one_or_none()
            
            if not chat:
                return False
            
            # Удаляем чат (каскадное удаление сработает из-за ondelete='CASCADE')
            delete_query = delete(ChatOrm).where(ChatOrm.id == chat_id)
            await session.execute(delete_query)
            await session.commit()
            
            return True




class MessageRepository:
    """Репозиторий для работы с сообщениями"""
    
    
    @classmethod
    async def send_message(
        cls, 
        message_data: MessageCreate, 
        sender_id: int
    ) -> Dict[str, Any]:
        """Отправляет сообщение в чат"""
        async with new_session() as session:
            # Проверяем, является ли отправитель участником чата
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == message_data.chat_id,
                ChatParticipantOrm.user_id == sender_id
            )
            participant_result = await session.execute(participant_query)
            if not participant_result.scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")
            
            # Проверяем reply_to_id
            if message_data.reply_to_id:
                reply_query = select(MessageOrm).where(
                    MessageOrm.id == message_data.reply_to_id,
                    MessageOrm.chat_id == message_data.chat_id
                )
                reply_result = await session.execute(reply_query)
                if not reply_result.scalar_one_or_none():
                    raise ValueError("Сообщение для ответа не найдено")
            
            # Проверяем file_id
            if message_data.file_id:
                file_query = select(FileOrm).where(FileOrm.id == message_data.file_id)
                file_result = await session.execute(file_query)
                if not file_result.scalar_one_or_none():
                    raise ValueError("Файл не найден")
            
            # Создаем сообщение
            message = MessageOrm(
                chat_id=message_data.chat_id,
                sender_id=sender_id,
                message_type=message_data.message_type,
                content=message_data.content,
                file_id=message_data.file_id,
                reply_to_id=message_data.reply_to_id,
                status=MessageStatus.SENT
            )
            
            session.add(message)
            
            # Обновляем время обновления чата
            update_chat_query = update(ChatOrm).where(
                ChatOrm.id == message_data.chat_id
            ).values(updated_at=datetime.now(timezone.utc))
            
            await session.execute(update_chat_query)
            await session.commit()
            
            # Получаем полную информацию о сообщении
            return await cls._get_message_by_id(message.id)
    
    
    @classmethod
    async def _get_message_by_id(cls, message_id: int) -> Optional[Dict[str, Any]]:
        """Получает сообщение по ID"""
        async with new_session() as session:
            message_query = select(MessageOrm).where(MessageOrm.id == message_id)
            message_result = await session.execute(message_query)
            message = message_result.scalar_one_or_none()
            
            if not message:
                return None
            
            return await cls._message_to_dict(message)
    
    
    @classmethod
    async def _message_to_dict(cls, message: MessageOrm) -> Dict[str, Any]:
        """Конвертирует объект MessageOrm в словарь"""
        async with new_session() as session:
            # Получаем информацию об отправителе
            sender_query = select(
                UserOrm.username, UserOrm.avatar_id,
                UserOrm.user_metadata
            ).where(UserOrm.id == message.sender_id)
            
            sender_result = await session.execute(sender_query)
            sender_row = sender_result.first()
            
            sender_username = None
            sender_avatar_url = None
            sender_metadata = None
            
            if sender_row:
                sender_username = sender_row.username
                sender_avatar_url = await cls._get_user_avatar_url(sender_row.avatar_id)
                sender_metadata = sender_row.user_metadata
            
            # Получаем информацию о файле
            file_url = None
            if message.file_id:
                file_query = select(FileOrm.filename).where(FileOrm.id == message.file_id)
                file_result = await session.execute(file_query)
                filename = file_result.scalar_one_or_none()
                
                if filename:
                    try:
                        file_url = await minio.get_url(filename)
                    except Exception:
                        pass
            
            return {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "sender_username": sender_username,
                "sender_avatar_url": sender_avatar_url,
                "sender_metadata": sender_metadata,
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
                return await minio.get_url(filename)
            except Exception:
                return None
    
    
    @classmethod
    async def get_messages(
        cls, 
        chat_id: int, 
        user_id: int,
        skip: int = 0, 
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Получает историю сообщений в чате"""
        async with new_session() as session:
            # Проверяем, является ли пользователь участником чата
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == user_id
            )
            participant_result = await session.execute(participant_query)
            if not participant_result.scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")
            
            # Базовый запрос для сообщений
            query = select(MessageOrm).where(
                MessageOrm.chat_id == chat_id
            ).order_by(desc(MessageOrm.created_at))
            
            if before:
                query = query.where(MessageOrm.created_at < before)
            
            # Общее количество сообщений
            count_query = select(func.count(MessageOrm.id)).where(
                MessageOrm.chat_id == chat_id
            )
            if before:
                count_query = count_query.where(MessageOrm.created_at < before)
            
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0
            
            # Получаем сообщения
            messages_query = query.offset(skip).limit(limit)
            messages_result = await session.execute(messages_query)
            messages = messages_result.scalars().all()
            
            # Конвертируем в словари
            messages_dict = []
            for message in reversed(messages):  # Возвращаем в правильном порядке
                messages_dict.append(await cls._message_to_dict(message))
            
            # Помечаем сообщения как прочитанные (игнорируем возвращаемый словарь, но метод может быть использован)
            await cls._mark_messages_as_read(chat_id, user_id, messages, session)
            
            return {
                "messages": messages_dict,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "page_size": limit,
                "has_more": (skip + limit) < total
            }
    
    
    @classmethod
    async def _mark_messages_as_read(
        cls, 
        chat_id: int, 
        user_id: int,
        messages: List[MessageOrm],
        session
    ) -> Dict[int, List[int]]:
        """
        Помечает сообщения как прочитанные и возвращает словарь {sender_id: [message_ids]}.
        """
        # Находим непрочитанные сообщения от других пользователей
        unread_message_ids = [
            msg.id for msg in messages 
            if msg.sender_id != user_id and msg.status in (MessageStatus.SENT, MessageStatus.DELIVERED)
        ]
        
        if not unread_message_ids:
            return {}
        
        # Получаем информацию об отправителях перед обновлением
        sender_query = select(MessageOrm.id, MessageOrm.sender_id).where(
            MessageOrm.id.in_(unread_message_ids)
        )
        sender_result = await session.execute(sender_query)
        sender_rows = sender_result.all()
        sender_map = {row.id: row.sender_id for row in sender_rows}
        
        # Обновляем статус сообщений
        update_query = update(MessageOrm).where(
            MessageOrm.id.in_(unread_message_ids)
        ).values(status=MessageStatus.READ)
        await session.execute(update_query)
        
        # Обновляем время последнего прочтения для участника
        update_participant_query = update(ChatParticipantOrm).where(
            ChatParticipantOrm.chat_id == chat_id,
            ChatParticipantOrm.user_id == user_id
        ).values(last_read_at=datetime.now(timezone.utc))
        await session.execute(update_participant_query)
        
        # Группируем по отправителям
        result = {}
        for msg_id, sender_id in sender_map.items():
            result.setdefault(sender_id, []).append(msg_id)
        
        return result
    
    
    @classmethod
    async def edit_message(
        cls, 
        message_id: int, 
        user_id: int,
        new_content: str
    ) -> Optional[Dict[str, Any]]:
        """Редактирует сообщение"""
        async with new_session() as session:
            # Получаем сообщение
            message_query = select(MessageOrm).where(MessageOrm.id == message_id)
            message_result = await session.execute(message_query)
            message = message_result.scalar_one_or_none()
            
            if not message or message.sender_id != user_id:
                return None
            
            # Проверяем, что сообщение не старше 24 часов
            time_diff = datetime.now(timezone.utc) - message.created_at
            if time_diff.total_seconds() > 24 * 3600:
                raise ValueError("Можно редактировать только сообщения младше 24 часов")
            
            # Обновляем сообщение
            message.content = new_content
            message.edited = True
            message.updated_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            return await cls._message_to_dict(message)
    
    
    @classmethod
    async def delete_message(
        cls, 
        message_id: int, 
        user_id: int
    ) -> Optional[int]:
        """Удаляет сообщение и возвращает chat_id в случае успеха"""
        async with new_session() as session:
            # Получаем сообщение
            message_query = select(MessageOrm).where(MessageOrm.id == message_id)
            message_result = await session.execute(message_query)
            message = message_result.scalar_one_or_none()
            
            if not message or message.sender_id != user_id:
                return None
            
            # Проверяем, что сообщение не старше 24 часов
            time_diff = datetime.now(timezone.utc) - message.created_at
            if time_diff.total_seconds() > 24 * 3600:
                raise ValueError("Можно удалять только сообщения младше 24 часов")
            
            chat_id = message.chat_id
            
            # Удаляем сообщение
            delete_query = delete(MessageOrm).where(MessageOrm.id == message_id)
            await session.execute(delete_query)
            await session.commit()
            
            return chat_id
    
    
    # Новые методы для статусов
    
    @classmethod
    async def mark_as_delivered(cls, message_ids: List[int], user_id: int, chat_id: int) -> List[int]:
        """
        Помечает сообщения как доставленные для указанного пользователя.
        Возвращает список ID сообщений, статус которых действительно изменился.
        """
        async with new_session() as session:
            # Проверяем, что пользователь является участником чата
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == user_id
            )
            if not (await session.execute(participant_query)).scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")
            
            # Обновляем только сообщения, которые были в статусе 'sent' и отправлены не этим пользователем
            query = update(MessageOrm).where(
                MessageOrm.id.in_(message_ids),
                MessageOrm.chat_id == chat_id,
                MessageOrm.sender_id != user_id,
                MessageOrm.status == MessageStatus.SENT
            ).values(status=MessageStatus.DELIVERED).returning(MessageOrm.id)
            
            result = await session.execute(query)
            updated_ids = result.scalars().all()
            await session.commit()
            return updated_ids
    
    
    @classmethod
    async def mark_as_read(cls, message_ids: List[int], user_id: int, chat_id: int) -> Dict[int, List[int]]:
        """
        Помечает сообщения как прочитанные.
        Возвращает словарь {sender_id: [message_ids]} для всех сообщений, статус которых изменился.
        """
        async with new_session() as session:
            # Проверяем участие в чате
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == user_id
            )
            if not (await session.execute(participant_query)).scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")
            
            # Получаем отправителей до обновления
            sender_query = select(MessageOrm.id, MessageOrm.sender_id).where(
                MessageOrm.id.in_(message_ids),
                MessageOrm.chat_id == chat_id,
                MessageOrm.sender_id != user_id,
                MessageOrm.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED])
            )
            sender_result = await session.execute(sender_query)
            sender_rows = sender_result.all()
            sender_map = {row.id: row.sender_id for row in sender_rows}
            
            if not sender_map:
                return {}
            
            # Обновляем статус
            update_query = update(MessageOrm).where(
                MessageOrm.id.in_(sender_map.keys())
            ).values(status=MessageStatus.READ)
            await session.execute(update_query)
            
            # Обновляем last_read_at
            update_participant = update(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == user_id
            ).values(last_read_at=datetime.now(timezone.utc))
            await session.execute(update_participant)
            
            await session.commit()
            
            # Группируем по отправителям
            result = {}
            for msg_id, sender_id in sender_map.items():
                result.setdefault(sender_id, []).append(msg_id)
            
            return result