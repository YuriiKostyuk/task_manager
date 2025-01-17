from enum import unique

from app.database.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """
        Модель пользователя (User) для базы данных.

        Атрибуты:
            id (int): Уникальный идентификатор пользователя.
            name (str): Имя пользователя (должно быть уникальным, максимум 100 символов).
            email (str): Email пользователя (уникальный).
            password (str): Хэшированный пароль пользователя.

        Связи:
            tasks: Связь с моделью Task (обратная связь через 'user').

        Таблица:
            users
        """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    tasks = relationship('Task', back_populates='user')
