import os

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import delete, select, update

from database import new_session
from models.auth import BlacklistedTokenOrm, RefreshTokenOrm, UserOrm
from models.files import FileOrm
from schemas.auth import SUserRegister, SRefreshToken
from utils.minio_client import minio




load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class UserRepository:
    """Репозиторий для работы с пользователями."""
    @classmethod
    async def register_user(cls, user_data: SUserRegister) -> int:
        """Регистрирует нового пользователя."""
        async with new_session() as session:
            if user_data.password != user_data.password_confirm:
                raise ValueError("Пароль и подтверждение пароля не совпадают")
            query = select(UserOrm).where(UserOrm.username == user_data.username)
            result = await session.execute(query)

            if result.scalars().first():
                raise ValueError("Пользователь с таким username уже существует")

            hashed_password = pwd_context.hash(user_data.password)

            user = UserOrm(
                username=user_data.username,
                hashed_password=hashed_password,
                is_online=False,
                last_seen=datetime.now(timezone.utc),
                user_metadata=user_data.user_metadata
            )

            session.add(user)
            await session.flush()
            await session.commit()

            return user.id


    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> UserOrm | None:
        """Аутентифицирует пользователя по username и паролю."""
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if not user or not pwd_context.verify(password, user.hashed_password):
                return None

            return user


    @classmethod
    async def get_user_by_username(cls, username: str) -> UserOrm | None:
        """Получает пользователя по username."""
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.username == username)
            result = await session.execute(query)

            return result.scalars().first()


    @classmethod
    async def get_user_by_id(cls, user_id: int) -> UserOrm | None:
        """Получает пользователя по ID."""
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.id == user_id)
            result = await session.execute(query)

            return result.scalars().first()


    @classmethod
    async def get_public_user_info(cls, user_id: int) -> dict | None:
        """Получает публичную информацию о пользователе по ID."""
        async with new_session() as session:
            query = select(
                UserOrm.id,
                UserOrm.username,
                UserOrm.avatar_id,
                UserOrm.bio,
                UserOrm.gender,
                UserOrm.birth_date,
                UserOrm.is_online,
                UserOrm.last_seen,
                UserOrm.created_at,
                UserOrm.user_metadata
            ).where(UserOrm.id == user_id)

            result = await session.execute(query)
            row = result.first()

            if not row:
                return None

            return {
                "id": row.id,
                "username": row.username,
                "avatar_id": row.avatar_id,
                "bio": row.bio,
                "gender": row.gender,
                "birth_date": row.birth_date,
                "is_online": row.is_online,
                "last_seen": row.last_seen,
                "created_at": row.created_at,
                "user_metadata": row.user_metadata
            }


    @classmethod
    async def get_user_status(cls, user_id: int) -> dict | None:
        """Получает статус пользователя (онлайн/оффлайн и последняя активность)."""
        async with new_session() as session:
            query = select(
                UserOrm.id,
                UserOrm.username,
                UserOrm.is_online,
                UserOrm.last_seen
            ).where(UserOrm.id == user_id)

            result = await session.execute(query)
            row = result.first()

            if not row:
                return None

            return {
                "user_id": row.id,
                "username": row.username,
                "is_online": row.is_online,
                "last_seen": row.last_seen
            }


    @classmethod
    async def update_user_status(cls, user_id: int, is_online: bool):
        """Обновляет статус пользователя (онлайн/оффлайн)."""
        async with new_session() as session:
            update_query = update(UserOrm).where(
                UserOrm.id == user_id
            ).values(
                is_online=is_online,
                last_seen=datetime.now(timezone.utc)
            )

            await session.execute(update_query)
            await session.commit()


    @classmethod
    async def get_user_by_refresh_token(cls, refresh_token_data: SRefreshToken) -> UserOrm | None:
        """Получает пользователя по refresh токену."""
        async with new_session() as session:
            refresh_token = refresh_token_data.refresh
            query = select(RefreshTokenOrm).where(RefreshTokenOrm.token == refresh_token)
            result = await session.execute(query)
            refresh_token_orm = result.scalars().first()

            if not refresh_token_orm or refresh_token_orm.expires_at < datetime.now(timezone.utc):
                return None

            return await cls.get_user_by_id(refresh_token_orm.user_id)


    @classmethod
    async def create_refresh_token(cls, user_id: int) -> str:
        """Создает новый refresh токен для пользователя."""
        async with new_session() as session:
            delete_query = delete(RefreshTokenOrm).where(RefreshTokenOrm.user_id == user_id)
            await session.execute(delete_query)

            refresh_token = jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)
            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            refresh_token_orm = RefreshTokenOrm(
                user_id=user_id,
                token=refresh_token,
                expires_at=expires_at
            )

            session.add(refresh_token_orm)
            await session.commit()

            return refresh_token


    @classmethod
    async def revoke_refresh_token(cls, user_id: int):
        """Отзывает refresh токен пользователя."""
        async with new_session() as session:
            query = delete(RefreshTokenOrm).where(RefreshTokenOrm.user_id == user_id)
            await session.execute(query)
            await session.commit()


    @classmethod
    async def add_to_blacklist(cls, token: str):
        """Добавляет токен в черный список."""
        async with new_session() as session:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

            except JWTError:
                return

            blacklisted_token = BlacklistedTokenOrm(
                token=token,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc)
            )

            session.add(blacklisted_token)
            await session.commit()


    @classmethod
    async def update_user(cls, user_id: int, update_data: dict) -> UserOrm | None:
        """Обновляет данные пользователя."""
        async with new_session() as session:
            query = select(UserOrm).where(UserOrm.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

            if not user:
                return None

            # Обновляем только переданные поля
            for key, value in update_data.items():
                if value is not None:
                    setattr(user, key, value)

            await session.commit()
            await session.refresh(user)

            return user


    @classmethod
    async def get_user_with_avatar_url(cls, user_id: int) -> dict | None:
        """Получает пользователя с URL аватарки."""
        async with new_session() as session:
            query = select(
                UserOrm.id,
                UserOrm.username,
                UserOrm.avatar_id,
                UserOrm.bio,
                UserOrm.gender,
                UserOrm.birth_date,
                UserOrm.is_online,
                UserOrm.last_seen,
                UserOrm.created_at,
                FileOrm.filename,
                UserOrm.user_metadata
            ).outerjoin(
                FileOrm, UserOrm.avatar_id == FileOrm.id
            ).where(UserOrm.id == user_id)

            result = await session.execute(query)
            row = result.first()

            if not row:
                return None

            user_data = {
                "id": row.id,
                "username": row.username,
                "avatar_id": row.avatar_id,
                "bio": row.bio,
                "gender": row.gender,
                "birth_date": row.birth_date,
                "is_online": row.is_online,
                "last_seen": row.last_seen,
                "created_at": row.created_at,
                "user_metadata": row.user_metadata
            }

            # Если есть аватарка, генерируем URL
            if row.filename:
                try:
                    user_data["avatar_url"] = await minio.get_url(row.filename)
                except Exception:
                    user_data["avatar_url"] = None
            else:
                user_data["avatar_url"] = None

            return user_data