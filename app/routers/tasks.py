from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from app.models.tasks import Task
from app.schemas import CreateTask, ReadTask, UpdateTask
from app.database.db_session import get_db
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
        task: CreateTask,
        db: AsyncSession = Depends(get_db),
        user: dict = Depends(get_current_user),
):
    user_id = user["id"]
    if task.status not in ["Новая", "В процессе", "Завершена"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недопустимый статус задачи")
    if (await db.execute(select(Task).where(Task.title == task.title))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такая задача уже есть")

    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL, detail="Ошибка при добавлении задачи в базу данных")
    return db_task

@router.get("/", response_model=List[ReadTask])
async def read_task(
        db: AsyncSession = Depends(get_db),
        user: dict = Depends(get_current_user),
):
    user_id = user["id"]
    query = select(Task).where(Task.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=ReadTask)
async def get_task_id(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        user: dict[str, int] = Depends(get_current_user),
) -> ReadTask:
    user_id = user["id"]
    query  = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    return task


@router.put("/{task_id}", response_model=UpdateTask)
async def update_task(
        task_id: int,
        task: UpdateTask,
        db: AsyncSession = Depends(get_db),
        user: dict = Depends(get_current_user),
):
    user_id = user["id"]
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    db_task = result.scalars().first()

    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL, detail="Ошибка при обновлении задачи")

    return db_task


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    query = select(Task).where(Task.id == task_id, Task.user_id == user['id'])
    result = await db.execute(query)
    db_task = result.scalars().first()

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    await db.delete(db_task)
    await db.commit()
    return {"detail": "Задача удалена"}

