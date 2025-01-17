import pytest
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.main import app
from app.models.users import User
from app.database.db import get_db

from passlib.context import CryptContext
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.models.users import User
from app.main import app
import pytest
from httpx import AsyncClient
from fastapi import status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Возвращает хэш пароля.

    Args:
        password (str): Оригинальный пароль.

    Returns:
        str: Хэшированный пароль.
    """
    return pwd_context.hash(password)


@pytest.fixture
async def access_token(client: TestClient, test_user: User) -> str:
    """
    Получает JWT токен для тестового пользователя.

    Args:
        client (TestClient): Тестовый клиент для выполнения HTTP-запросов.
        test_user (User): Тестовый пользователь, для которого запрашивается токен.

    Returns:
        str: Токен доступа.

    Raises:
        AssertionError: Если запрос на получение токена завершился с ошибкой.
    """
    response = await client.post("/auth/token", data={
        "username": test_user.name,
        "password": "testpassword"
    })
    assert response.status_code == 200
    token = response.json().get("access_token")
    return token


@pytest.fixture(scope='function')
async def db_session() -> AsyncSession:
    """
    Создаёт сессию базы данных для тестов.

    Yields:
        AsyncSession: Сессия базы данных.

    Notes:
        После завершения теста сессия автоматически закрывается.
    """
    db_gen = get_db()
    async for session in db_gen:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """
    Создаёт тестового пользователя в базе данных.

    Args:
        db_session (AsyncSession): Сессия базы данных.

    Yields:
        User: Тестовый пользователь.

    Notes:
        После завершения теста пользователь удаляется из базы данных.
    """
    user = User(name="testuser", password=get_password_hash('testpassword'),
                email="testuser@mail.com")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    try:
        await db_session.delete(user)
        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise
    finally:
        await db_session.rollback()


@pytest.fixture
async def client() -> AsyncClient:
    """
    Создаёт тестовый клиент для FastAPI приложения.

    Yields:
        AsyncClient: Тестовый HTTP клиент.

    Notes:
        Клиент автоматически закрывается после завершения теста.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user: User):
    """
    Тест успешной авторизации.

    Проверяет, что авторизация возвращает корректный JWT токен.

    Args:
        client (AsyncClient): Тестовый HTTP клиент.
        test_user (User): Тестовый пользователь.

    Raises:
        AssertionError: Если авторизация не прошла успешно.
    """
    response = await client.post("/auth/token", data={
        "username": test_user.name,
        "password": "testpassword"
    })
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_read_current_user_without_token(client: AsyncClient):
    """
    Тест проверки доступа к защищённому маршруту без токена.

    Проверяет, что запрос завершается с кодом 401 (Unauthorized).

    Args:
        client (AsyncClient): Тестовый HTTP клиент.

    Raises:
        AssertionError: Если запрос не завершился с кодом 401.
    """
    response = await client.get("/auth/read_current_user")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_current_user_with_token(client: AsyncClient, test_user: User, access_token: str):
    """
    Тест успешного доступа к защищённому маршруту с токеном.

    Проверяет, что возвращается информация о текущем пользователе.

    Args:
        client (AsyncClient): Тестовый HTTP клиент.
        test_user (User): Тестовый пользователь.
        access_token (str): Токен доступа.

    Raises:
        AssertionError: Если запрос не прошёл успешно или данные пользователя не совпадают.
    """
    response = await client.get("/auth/read_current_user", headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()
    assert "username" in data["User"]
    assert data["User"]["username"] == test_user.name
    assert response.status_code == status.HTTP_200_OK
