import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase




load_dotenv()

engine = create_async_engine(os.getenv('DATABASE_URL'))

new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""
    pass




async def create_tables():
    """Создает все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    """Удаляет все таблицы из базы данных (только для тестов)."""
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)