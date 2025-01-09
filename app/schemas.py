from email.policy import default

from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Literal


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
            status (str): Статус задачи.
        """
    id: int
    title: str
    description: Optional[str] = None
    status: str


class CreateTask(BaseModel):
    """
        Схема для создания новой задачи.

        Атрибуты:
            title (str): Заголовок задачи.
            description (Optional[str]): Описание задачи.
            status (Literal): Статус задачи (по умолчанию "Новая").
        """
    title: str
    description: Optional[str] = None
    status: Literal["Новая", "В процессе", "Завершена"] = "Новая"


class UpdateTask(BaseModel):
    """
        Схема для обновления статуса задачи.

        Атрибуты:
            status (str): Новый статус задачи.
        """
    status: str
