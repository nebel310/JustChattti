from sqlalchemy import select
from datetime import datetime, timezone
from database import new_session
from models.auth import UserOrm, UserRole
from passlib.context import CryptContext




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



async def create_admin():
    """Функция для создания первого администратора"""
    async with new_session() as session:
        username = "admin"
        password = "admin"
        role = UserRole.ADMIN
        metadata = {"key": "value"}
        
        query = select(UserOrm).where(UserOrm.username == username)
        result = await session.execute(query)
        user = result.scalars().first()
        
        if not user:
            hashed_password = pwd_context.hash(password)  # Хэшируем пароль
            user = UserOrm(
                username=username,
                hashed_password=hashed_password,
                role=role,
                is_online=False,
                last_seen=datetime.now(timezone.utc),
                user_metadata=metadata
            )
            session.add(user)
            await session.commit()