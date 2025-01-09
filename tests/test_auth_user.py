import pytest
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.main import app
from app.models.users import User
from app.database.db_session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """
        Возвращает хэш пароля.

        Аргументы:
            password (str): Оригинальный пароль.

        Returns:
            str: Хэшированный пароль.
        """
    return pwd_context.hash(password)


@pytest.fixture
async def access_token(client, test_user):
    """
        Получает JWT токен для тестового пользователя.

        Возвращает:
            str: Токен доступа.
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

        Возвращает:
            AsyncSession: Сессия базы данных.
        """
    db_gen = get_db()
    async for session in db_gen:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """
       Создаёт тестового пользователя в базе данных.

       Возвращает:
           User: Тестовый пользователь.
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
async def client():
    """
        Создаёт тестовый клиент для FastAPI приложения.

        Возвращает:
            AsyncClient: Тестовый HTTP клиент.
        """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_login(client, test_user):
    """
        Тест успешной авторизации.

        Проверяет, что авторизация возвращает корректный JWT токен.
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
        Тест проверки доступа к защищенному маршруту без токена.

        Ожидается, что запрос завершится с кодом 401.
        """
    response = await client.get("/auth/read_current_user")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_current_user_with_token(client: AsyncClient, test_user: User, access_token):
    """
        Тест успешного доступа к защищенному маршруту с токеном.

        Проверяет, что возвращается информация о текущем пользователе.
        """
    response = await client.get("/auth/read_current_user", headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()
    assert "username" in data["User"]
    assert data["User"]["username"] == test_user.name
    assert response.status_code == status.HTTP_200_OK
