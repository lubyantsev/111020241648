from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from app.backend.db_depends import get_db

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/", response_model=list[Task])
async def all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks


@router.get("/{task_id}", response_model=Task)
async def task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task(create_task: CreateTask, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    # Создание новой задачи
    new_task = Task(**create_task.dict(), user_id=user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update/{task_id}", response_model=Task)
async def update_task(task_id: int, update_task: UpdateTask, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in update_task.dict().items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()