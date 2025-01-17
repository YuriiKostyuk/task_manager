import httpx
import pytest

import pytest


@pytest.mark.asyncio
async def test_create_user(test_client, user_payload):
    """
    Тест успешного создания пользователя.

    Проверяет, что:
    1. Запрос на создание пользователя возвращает статус код 201 (Created).
    2. Ответ содержит данные созданного пользователя, включая имя и email.

    Args:
        test_client: Тестовый клиент для выполнения HTTP-запросов.
        user_payload (dict): Данные для создания пользователя.

    Raises:
        AssertionError: Если запрос не прошёл успешно или данные пользователя не совпадают.
    """
    response = await test_client.post("/users/", json=user_payload)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == user_payload["name"]
    assert response_data["email"] == user_payload["email"]


@pytest.mark.asyncio
async def test_create_user_missing_data(test_client, invalid_user_payload):
    """
    Тест создания пользователя с недостающими данными.

    Проверяет, что:
    1. Запрос на создание пользователя с недостающими данными возвращает статус код 422 (Unprocessable Entity).
    2. Ответ содержит поле "detail" с описанием ошибки.

    Args:
        test_client: Тестовый клиент для выполнения HTTP-запросов.
        invalid_user_payload (dict): Неполные или некорректные данные для создания пользователя.

    Raises:
        AssertionError: Если запрос не завершился с кодом 422 или ответ не содержит поля "detail".
    """
    response = await test_client.post("/users/", json=invalid_user_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_user_duplicate(test_client, user_payload):
    """
    Тест создания пользователя с дублирующимся email.

    Проверяет, что:
    1. Запрос на создание пользователя с уже существующим email возвращает статус код 400 (Bad Request).
    2. Ответ содержит поле "detail" с описанием ошибки.

    Args:
        test_client: Тестовый клиент для выполнения HTTP-запросов.
        user_payload (dict): Данные для создания пользователя.

    Raises:
        AssertionError: Если запрос не завершился с кодом 400 или ответ не содержит поля "detail".
    """
    response = await test_client.post("/users/", json=user_payload)
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
