from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal
import loguru


async def get_db() -> AsyncSession:
    """
        Создаёт асинхронную сессию базы данных.

        Предоставляет асинхронную сессию для взаимодействия с базой данных с использованием контекстного менеджера.
        В случае возникновения исключений, выполняет откат транзакции и логирует сообщение об ошибке.

        Returns:
            AsyncSession: Асинхронная сессия базы данных.

        Исключения:
            SQLAlchemyError: Ошибка, возникающая при работе с базой данных.

        Пример использования:
            async for db in get_db():
                # Ваш код взаимодействия с базой данных
        """
    async with SessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            loguru.logger.error(f"Ошибка сессии: {e}")
            await session.rollback()
            raise
