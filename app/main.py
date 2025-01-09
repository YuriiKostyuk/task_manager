from fastapi import FastAPI

from app.routers import users
from app.routers import tasks
from app.routers import auth

app = FastAPI(
    title="Task Management API",
    description="API для управления задачами и пользователями",
    version="1.0.0",
)

# Подключение маршрутов из модулей
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(auth.router)


@app.get('/')
async def health_check():
    """
    Точка доступа для проверки работоспособности API.

    Возвращает:
        dict: Статус приложения и текущая версия.

    Пример ответа:
    ```
    {
        "status": "healthy",
        "version": "1.0.0"
    }
    ```
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
