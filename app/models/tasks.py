from app.database.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Task(Base):
    """
        Модель задачи (Task) для базы данных.

        Атрибуты:
            id (int): Уникальный идентификатор задачи.
            title (str): Название задачи (максимум 50 символов).
            description (str): Описание задачи (максимум 255 символов).
            status (str): Статус задачи (например, "выполнено", "в процессе").
            user_id (int): Идентификатор пользователя, которому принадлежит задача.

        Связи:
            user: Связь с моделью User (обратная связь через 'tasks').

        Таблица:
            tasks
        """
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='tasks')
