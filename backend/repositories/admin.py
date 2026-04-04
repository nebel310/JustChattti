from sqlalchemy import update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import new_session
from models.auth import UserOrm
from schemas.admin import SChangeRole, SChangeStorageLimit, ChangeRoleResponse, ChangeStorageLimitResponse




class AdminRepository:
    """Репозиторий с логикой для админских роутов"""
    @classmethod
    async def change_user_role(cls, change_data: SChangeRole) -> ChangeRoleResponse:
        """Метод для изменения роли пользователя"""
        async with new_session() as session:
            user = await session.get(UserOrm, change_data.user_id)
            if not user:
                raise ValueError("Пользователь не найден")
            
            query = update(UserOrm).where(
                UserOrm.id == change_data.user_id
            ).values(
                role=change_data.new_user_role
            )

            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError as e:
                raise ValueError("Нарушение целостности данных") from e
            except SQLAlchemyError as e:
                raise ValueError(f"Ошибка базы данных: {str(e)}") from e
            
        return ChangeRoleResponse(
            success=True,
            user_id=change_data.user_id,
            role=change_data.new_user_role.value
        )
    
    
    @classmethod
    async def change_user_storage_limit(cls, change_data: SChangeStorageLimit) -> ChangeStorageLimitResponse:
        """Метод для изменения лимита хранилища пользователя"""
        async with new_session() as session:
            user = await session.get(UserOrm, change_data.user_id)
            if not user:
                raise ValueError("Пользователь не найден")
            
            # Проверяем, что новый лимит не меньше уже использованного места
            if change_data.new_storage_limit_bytes < user.storage_used_bytes:
                raise ValueError(
                    f"Новый лимит ({change_data.new_storage_limit_bytes} байт) "
                    f"не может быть меньше уже использованного места ({user.storage_used_bytes} байт)"
                )
            
            query = update(UserOrm).where(
                UserOrm.id == change_data.user_id
            ).values(
                storage_limit_bytes=change_data.new_storage_limit_bytes
            )
            
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError as e:
                raise ValueError("Нарушение целостности данных") from e
            except SQLAlchemyError as e:
                raise ValueError(f"Ошибка базы данных: {str(e)}") from e
            
        return ChangeStorageLimitResponse(
            success=True,
            user_id=change_data.user_id,
            storage_limit_bytes=change_data.new_storage_limit_bytes
        )