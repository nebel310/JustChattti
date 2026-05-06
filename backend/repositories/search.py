from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, or_, and_, text, desc

from database import new_session
from models.auth import UserOrm
from models.chat import MessageOrm, ChatParticipantOrm
from models.files import FileOrm
from utils.cursor import encode_cursor, decode_cursor
from utils.minio_client import minio




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
                UserOrm.last_seen,
                UserOrm.user_metadata
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
                    "user_metadata": row.user_metadata,
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
                UserOrm.last_seen,
                UserOrm.user_metadata
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
                    "user_metadata": row.user_metadata,
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
        limit: int = 50,
        cursor: Optional[str] = None,
        direction: str = "before"
    ) -> Dict[str, Any]:
        async with new_session() as session:
            user_chats_subquery = select(ChatParticipantOrm.chat_id).where(
                ChatParticipantOrm.user_id == current_user_id
            ).subquery()

            tsquery = func.plainto_tsquery(text("'simple'"), text_query)
            base_condition = and_(
                MessageOrm.chat_id.in_(user_chats_subquery),
                func.to_tsvector('simple', MessageOrm.content).op('@@')(tsquery)
            )

            query = select(MessageOrm).where(base_condition)

            cursor_created_at = None
            cursor_id = None
            if cursor:
                cursor_created_at, cursor_id = decode_cursor(cursor)

            if direction == "before":
                order_by = [MessageOrm.created_at.desc(), MessageOrm.id.desc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at < cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id < cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at < cursor_created_at)
            else:  # "after"
                order_by = [MessageOrm.created_at.asc(), MessageOrm.id.asc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at > cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id > cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at > cursor_created_at)

            query = query.order_by(*order_by)
            messages_query = query.limit(limit + 1)
            result = await session.execute(messages_query)
            messages = result.scalars().all()

            has_more = len(messages) > limit
            next_cursor = None
            prev_cursor = None

            if has_more:
                messages = messages[:limit]
                last_visible = messages[-1]
                if direction == "before":
                    next_cursor = encode_cursor(last_visible.created_at, last_visible.id)
                else:
                    prev_cursor = encode_cursor(last_visible.created_at, last_visible.id)
            else:
                messages = messages[:limit]

            if direction == "before":
                messages_dict = await cls._messages_to_dicts(list(reversed(messages)), session)
            else:
                messages_dict = await cls._messages_to_dicts(messages, session)

            total = 0
            if cursor is None:
                count_query = select(func.count()).select_from(MessageOrm).where(base_condition)
                total = (await session.execute(count_query)).scalar() or 0

            return {
                "messages": messages_dict,
                "total": total,
                "page": None,
                "page_size": limit,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "prev_cursor": prev_cursor,
            }
                
    
    @classmethod
    async def search_messages_in_chat(
        cls,
        current_user_id: int,
        chat_id: int,
        text_query: str,
        limit: int = 50,
        cursor: Optional[str] = None,
        direction: str = "before"
    ) -> Dict[str, Any]:
        async with new_session() as session:
            participant_query = select(ChatParticipantOrm).where(
                ChatParticipantOrm.chat_id == chat_id,
                ChatParticipantOrm.user_id == current_user_id
            )
            if not (await session.execute(participant_query)).scalar_one_or_none():
                raise ValueError("Пользователь не является участником чата")

            tsquery = func.plainto_tsquery(text("'simple'"), text_query)
            base_condition = and_(
                MessageOrm.chat_id == chat_id,
                func.to_tsvector('simple', MessageOrm.content).op('@@')(tsquery)
            )

            query = select(MessageOrm).where(base_condition)

            cursor_created_at = None
            cursor_id = None
            if cursor:
                cursor_created_at, cursor_id = decode_cursor(cursor)

            if direction == "before":
                order_by = [MessageOrm.created_at.desc(), MessageOrm.id.desc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at < cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id < cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at < cursor_created_at)
            else:
                order_by = [MessageOrm.created_at.asc(), MessageOrm.id.asc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at > cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id > cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at > cursor_created_at)

            query = query.order_by(*order_by)
            messages_query = query.limit(limit + 1)
            result = await session.execute(messages_query)
            messages = result.scalars().all()

            has_more = len(messages) > limit
            next_cursor = None
            prev_cursor = None

            if has_more:
                messages = messages[:limit]
                last_visible = messages[-1]
                if direction == "before":
                    next_cursor = encode_cursor(last_visible.created_at, last_visible.id)
                else:
                    prev_cursor = encode_cursor(last_visible.created_at, last_visible.id)
            else:
                messages = messages[:limit]

            if direction == "before":
                messages_dict = await cls._messages_to_dicts(list(reversed(messages)), session)
            else:
                messages_dict = await cls._messages_to_dicts(messages, session)

            total = 0
            if cursor is None:
                count_query = select(func.count()).select_from(MessageOrm).where(base_condition)
                total = (await session.execute(count_query)).scalar() or 0

            return {
                "messages": messages_dict,
                "total": total,
                "page": None,
                "page_size": limit,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "prev_cursor": prev_cursor,
            }
            
                
    @classmethod
    async def search_messages_by_username(
        cls,
        current_user_id: int,
        username_query: str,
        limit: int = 50,
        cursor: Optional[str] = None,
        direction: str = "before"
    ) -> Dict[str, Any]:
        async with new_session() as session:
            user_ids_query = select(UserOrm.id).where(
                UserOrm.username.ilike(f"%{username_query}%")
            )
            user_ids_result = await session.execute(user_ids_query)
            user_ids = [row.id for row in user_ids_result.all()]
            if not user_ids:
                return {
                    "messages": [],
                    "total": 0,
                    "page": None,
                    "page_size": limit,
                    "has_more": False,
                    "next_cursor": None,
                    "prev_cursor": None,
                }

            user_chats_subquery = select(ChatParticipantOrm.chat_id).where(
                ChatParticipantOrm.user_id == current_user_id
            ).subquery()

            base_condition = and_(
                MessageOrm.chat_id.in_(user_chats_subquery),
                MessageOrm.sender_id.in_(user_ids)
            )

            query = select(MessageOrm).where(base_condition)

            cursor_created_at = None
            cursor_id = None
            if cursor:
                cursor_created_at, cursor_id = decode_cursor(cursor)

            if direction == "before":
                order_by = [MessageOrm.created_at.desc(), MessageOrm.id.desc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at < cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id < cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at < cursor_created_at)
            else:
                order_by = [MessageOrm.created_at.asc(), MessageOrm.id.asc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at > cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id > cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at > cursor_created_at)

            query = query.order_by(*order_by)
            messages_query = query.limit(limit + 1)
            result = await session.execute(messages_query)
            messages = result.scalars().all()

            has_more = len(messages) > limit
            next_cursor = None
            prev_cursor = None

            if has_more:
                messages = messages[:limit]
                last_visible = messages[-1]
                if direction == "before":
                    next_cursor = encode_cursor(last_visible.created_at, last_visible.id)
                else:
                    prev_cursor = encode_cursor(last_visible.created_at, last_visible.id)
            else:
                messages = messages[:limit]

            if direction == "before":
                messages_dict = await cls._messages_to_dicts(list(reversed(messages)), session)
            else:
                messages_dict = await cls._messages_to_dicts(messages, session)

            total = 0
            if cursor is None:
                count_query = select(func.count()).select_from(MessageOrm).where(base_condition)
                total = (await session.execute(count_query)).scalar() or 0

            return {
                "messages": messages_dict,
                "total": total,
                "page": None,
                "page_size": limit,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "prev_cursor": prev_cursor,
            }


    @classmethod
    async def _messages_to_dicts(
        cls,
        messages: List[MessageOrm],
        session
    ) -> List[Dict[str, Any]]:
        """Конвертирует список объектов MessageOrm в список словарей с контекстными курсорами (указывающими на само сообщение)"""
        messages_dicts = []
        for message in messages:
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

            # Контекстный курсор указывает на само сообщение
            context_cursor = encode_cursor(message.created_at, message.id)

            message_dict = {
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
                "updated_at": message.updated_at,
                "context_prev_cursor": context_cursor,
                "context_next_cursor": context_cursor,
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
                return await minio.get_url(filename)
            except Exception:
                return None
            
            
    @classmethod
    async def search_messages_by_sender(
        cls,
        current_user_id: int,
        sender_id: int,
        text_query: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[str] = None,
        direction: str = "before"
    ) -> Dict[str, Any]:
        async with new_session() as session:
            user_chats_subquery = select(ChatParticipantOrm.chat_id).where(
                ChatParticipantOrm.user_id == current_user_id
            ).subquery()

            conditions = [
                MessageOrm.chat_id.in_(user_chats_subquery),
                MessageOrm.sender_id == sender_id
            ]

            if text_query:
                tsquery = func.plainto_tsquery(text("'simple'"), text_query)
                conditions.append(
                    func.to_tsvector(text("'simple'"), MessageOrm.content).op('@@')(tsquery)
                )

            base_condition = and_(*conditions)
            query = select(MessageOrm).where(base_condition)

            cursor_created_at = None
            cursor_id = None
            if cursor:
                cursor_created_at, cursor_id = decode_cursor(cursor)

            if direction == "before":
                order_by = [MessageOrm.created_at.desc(), MessageOrm.id.desc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at < cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id < cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at < cursor_created_at)
            else:
                order_by = [MessageOrm.created_at.asc(), MessageOrm.id.asc()]
                if cursor_created_at is not None and cursor_id is not None:
                    query = query.where(
                        or_(
                            MessageOrm.created_at > cursor_created_at,
                            and_(
                                MessageOrm.created_at == cursor_created_at,
                                MessageOrm.id > cursor_id
                            )
                        )
                    )
                elif cursor_created_at is not None:
                    query = query.where(MessageOrm.created_at > cursor_created_at)

            query = query.order_by(*order_by)
            messages_query = query.limit(limit + 1)
            result = await session.execute(messages_query)
            messages = result.scalars().all()

            has_more = len(messages) > limit
            next_cursor = None
            prev_cursor = None

            if has_more:
                messages = messages[:limit]
                last_visible = messages[-1]
                if direction == "before":
                    next_cursor = encode_cursor(last_visible.created_at, last_visible.id)
                else:
                    prev_cursor = encode_cursor(last_visible.created_at, last_visible.id)
            else:
                messages = messages[:limit]

            if direction == "before":
                messages_dict = await cls._messages_to_dicts(list(reversed(messages)), session)
            else:
                messages_dict = await cls._messages_to_dicts(messages, session)

            total = 0
            if cursor is None:
                count_query = select(func.count()).select_from(MessageOrm).where(base_condition)
                total = (await session.execute(count_query)).scalar() or 0

            return {
                "messages": messages_dict,
                "total": total,
                "page": None,
                "page_size": limit,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "prev_cursor": prev_cursor,
            }