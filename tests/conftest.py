import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.db import Base
from app.database.db_session import get_db
import uuid

# Конфигурация тестовой базы данных
SQLITE_DATABASE_URL = "sqlite+aiosqlite:///./test_db.db"
unique_email = f"user_{uuid.uuid4()}@example.com"

engine = create_async_engine(
    SQLITE_DATABASE_URL,
    future=True,
    echo=False,
)

TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Создаёт таблицы базы данных перед началом тестов и удаляет их после завершения.

    Используется для глобальной настройки базы данных для всех тестов.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db():
    """
    Создаёт новую сессию базы данных для теста.

    Возвращает:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_client(db):
    """
        Создаёт тестовый клиент для взаимодействия с FastAPI приложением.

        Переопределяет зависимость базы данных `get_db` для изоляции тестов.

        Возвращает:
            AsyncClient: Тестовый HTTP клиент.
        """
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_payload():
    """
        Генерирует данные для создания пользователя.

        Возвращает:
            dict: Поля name, email и password.
        """
    return {
        "name": "testuser",
        "email": unique_email,
        "password": "securepassword",
    }


@pytest.fixture
def invalid_user_payload():
    """
        Генерирует некорректные данные для создания пользователя.

        Возвращает:
            dict: Некорректные значения полей name, email и password.
        """
    return {
        "name": "",
        "email": "invalid-email",
        "password": "short"
    }
