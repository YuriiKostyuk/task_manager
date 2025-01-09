import httpx
import pytest


@pytest.mark.asyncio
async def test_create_user(test_client, user_payload):
    """Тест успешного создания пользователя."""
    response = await test_client.post("/users/", json=user_payload)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == user_payload["name"]
    assert response_data["email"] == user_payload["email"]


@pytest.mark.asyncio
async def test_create_user_missing_data(test_client, invalid_user_payload):
    """Тест создания пользователя с некорректными данными."""
    response = await test_client.post("/users/", json=invalid_user_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_user_duplicate(test_client, user_payload):
    # Второй запрос — создание дубликата
    response = await test_client.post("/users/", json=user_payload)
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
