import re
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bcrypt_context
from app.database.db import get_db
from typing import Annotated
from app.models.users import User
from sqlalchemy import select
from app.schemas import CreateUser, ReadUser
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def is_password_strong(password: str) -> bool:
    """
    Проверяет, соответствует ли пароль требованиям сложности.

    Args:
        password (str): Пароль для проверки.

    Returns:
        bool: True, если пароль соответствует требованиям, иначе False.
    """
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?/~`]", password):
        return False

    return True


@router.get('/', response_model=list[ReadUser])
async def all_users(db: Annotated[AsyncSession, Depends(get_db)]):
    """
        Получает список всех пользователей.

        Args:
            db (AsyncSession): Сессия базы данных, полученная через dependency injection.

        Returns:
            list[ReadUser]: Список всех пользователей.

        Raises:
            HTTPException: Если пользователи не найдены (404) или произошла внутренняя ошибка сервера (500).
        """
    try:
        result = await db.scalars(select(User))
        users = result.all()

        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи не найдены")

        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{user_id}', response_model=ReadUser)
async def get_user_id(db: Annotated[AsyncSession, Depends(get_db)], user_id: int):
    """
        Получает информацию о пользователе по его ID.

        Args:
            db (AsyncSession): Сессия базы данных, полученная через dependency injection.
            user_id (int): ID пользователя.

        Returns:
            ReadUser: Информация о пользователе.

        Raises:
            HTTPException: Если пользователь не найден (404).
        """
    user = await db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return user


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CreateUser)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], user: CreateUser):
    """
        Создает нового пользователя.

        Args:
            db (AsyncSession): Сессия базы данных, полученная через dependency injection.
            user (CreateUser): Данные для создания нового пользователя.

        Returns:
            CreateUser: Созданный пользователь.

        Raises:
            HTTPException: Если пользователь с таким email уже существует (400).
        """

    if not is_password_strong(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль не соответствует требованиям"
        )

    hashed_password = bcrypt_context.hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот пользователь уже существует"
        )

    return new_user


@router.put('/{user_id}', response_model=ReadUser)
async def update_user(
        user_id: int,
        update_user: CreateUser,
        db: AsyncSession = Depends(get_db),
):
    """
        Обновляет информацию о пользователе по его ID.

        Args:
            user_id (int): ID пользователя, которого нужно обновить.
            update_user (CreateUser): Новые данные для обновления пользователя.
            db (AsyncSession): Сессия базы данных, полученная через dependency injection.

        Returns:
            ReadUser: Обновленная информация о пользователе.

        Raises:
            HTTPException: Если пользователь не найден (404) или пользователь с таким email уже существует (400).
        """
    user = await  db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if update_user.password and not is_password_strong(update_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль не соответствует требованиям"
        )

    if update_user.password:
        user.password = bcrypt_context.hash(update_user.password)
    user.name = update_user.name
    user.email = update_user.email

    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с такой почтой уже сущеcтвует"
        )

    return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int):
    """
        Удаляет пользователя по его ID.

        Args:
            db (AsyncSession): Сессия базы данных, полученная через dependency injection.
            user_id (int): ID пользователя, которого нужно удалить.

        Returns:
            dict: Сообщение об успешном удалении пользователя.

        Raises:
            HTTPException: Если пользователь не найден (404).
        """
    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    await db.delete(user)
    await db.commit()

    return {'detail': "Пользователь удален"}
