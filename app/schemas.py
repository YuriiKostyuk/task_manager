from enum import Enum
from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class TaskStatus(str, Enum):
    NEW = "Новая"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершена"


class ReadUser(BaseModel):
    """
    Схема для чтения данных пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        name (str): Имя пользователя.
        email (EmailStr): Email пользователя.
    """
    id: int
    name: str
    email: EmailStr


class CreateUser(BaseModel):
    """
    Схема для создания нового пользователя.

    Атрибуты:
        name (str): Имя пользователя.
        email (EmailStr): Email пользователя.
        password (constr): Пароль (минимум 5 символов).
    """
    name: str
    email: EmailStr
    password: constr(min_length=5)


class ReadTask(BaseModel):
    """
    Схема для чтения данных задачи.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        title (str): Заголовок задачи.
        description (Optional[str]): Описание задачи.
        status (TaskStatus): Статус задачи.
    """
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus


class CreateTask(BaseModel):
    """
    Схема для создания новой задачи.

    Атрибуты:
        title (str): Заголовок задачи.
        description (Optional[str]): Описание задачи.
        status (TaskStatus): Статус задачи (по умолчанию "Новая").
    """
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NEW


class UpdateTask(BaseModel):
    """
    Схема для обновления статуса задачи.

    Атрибуты:
        status (TaskStatus): Новый статус задачи.
    """
    status: TaskStatus = TaskStatus.NEW
