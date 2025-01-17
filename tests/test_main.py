import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.anyio
async def test_root():
    """
    Тестирует корневой эндпоинт (/).

    Проверяет, что:
    1. Эндпоинт возвращает статус код 200 (успешный запрос).
    2. Ответ содержит JSON с ключами "status" и "version", где:
       - "status" равен "healthy".
       - "version" равен "1.0.0".

    Использует AsyncClient для выполнения асинхронного HTTP-запроса к приложению.
    """
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": "1.0.0"
    }
