from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.models.users import User
from app.database.db_session import get_db
from typing import Annotated
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import SECRET_KEY, ALGORITHM, bcrypt_context, oauth2_scheme

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)

async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], user_name: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.name == user_name))
    if not user or not bcrypt_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Данные некорректны"
        )
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get('sub')
        user_id: int = payload.get('id')
        expire = payload.get('exp')

        if name is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Не удалось проверить пользователя'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не предоставлен токен доступа"
            )
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Токен истёк!"
            )

        return {
            'username': name,
            'id': user_id,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось проверить пользователя'
        )


async def create_access_token(name: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': name, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {"User": user}


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )
    token = await create_access_token(user.name, user.id, expires_delta=timedelta(minutes=15))
    return {
        "access_token": token,
        "token_type": "bearer",
    }