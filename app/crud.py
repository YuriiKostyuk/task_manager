import os
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Any, Dict, Annotated
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

# Инициализация шифрования для паролей
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка схемы OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Секретный ключ для токенов и алгоритм шифрования
SECRET_KEY = os.getenv("SECRET_KEY", 'your_default_secret_key')
ALGORITHM = "HS256"


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
        Создаёт JWT токен для авторизации.

        Аргументы:
            data (dict): Данные для шифрования в токене (например, имя пользователя и ID).
            expires_delta (timedelta, optional): Время жизни токена. Если не указано, токен будет действителен 15 минут.

        Returns:
            str: JWT токен.

        Пример:
            create_access_token({"sub": "username", "id": 1})
        """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def verify_access_token(token: str) -> Dict[str, Any]:
    """
        Проверяет и декодирует JWT токен.

        Аргументы:
            token (str): JWT токен для проверки.

        Returns:
            dict: Декодированные данные из токена.

        Исключения:
            HTTPException: Если токен недействителен или отсутствует.

        Пример:
            verify_access_token(token)
        """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Токен пустой"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Недействительный токе"
        )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
        Получает текущего авторизованного пользователя на основе JWT токена.

        Аргументы:
            token (str): JWT токен, переданный через схему OAuth2.

        Returns:
            dict: Данные текущего пользователя (имя пользователя и ID).

        Исключения:
            HTTPException: Если токен недействителен, истёк или пользователь не авторизован.

        Пример:
            user = await get_current_user(token)
        """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь неавторизован"
        )
    name: str = payload.get("sub")
    user_id: int = payload.get("id")
    expire = payload.get("exp")
    if name is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь неавторизован"
        )
    if expire is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ошибка срока токена"
        )
    if datetime.now() > datetime.fromtimestamp(expire):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Истек срок токена"
        )
    return {
        "username": name,
        "id": user_id,
    }


async def generate_access_token(name: str, user_id: int, expires_delta: timedelta | None = None):
    """
        Генерирует JWT токен для указанного пользователя.

        Аргументы:
            name (str): Имя пользователя.
            user_id (int): Идентификатор пользователя.
            expires_delta (timedelta, optional): Время жизни токена. Если не указано, токен будет действителен 15 минут.

        Returns:
            str: Сгенерированный JWT токен.

        Пример:
            token = await generate_access_token("username", 1)
        """
    data = {"sub": name, "id": user_id}
    return create_access_token(data, expires_delta)
