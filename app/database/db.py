import os
import loguru

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# URL для подключения к базе данных (по умолчанию SQLite, если переменная окружения DATABASE_URL не задана)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Создание асинхронного движка базы данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика для создания асинхронных сессий базы данных
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def check_connection():
    """
       Проверяет подключение к базе данных.

       Выполняет тестовый запрос к базе данных (`SELECT 1`) для проверки доступности подключения.
       Если подключение успешно, логирует сообщение об успехе.
       В случае ошибки логирует сообщение об ошибке.

       Пример использования:
           await check_connection()
       """
    try:
        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))
            loguru.logger.info("Успешное подключение к базе данных")
    except Exception as e:
        loguru.logger.error(f"Ошибка подключения к базе данных: {e}")


class Base(DeclarativeBase):
    """
        Базовый класс для всех моделей SQLAlchemy.

        Используется для декларативного определения таблиц и моделей.
        Все модели базы данных должны наследовать этот класс.
        """
    pass
