from fastapi import FastAPI, HTTPException, Path, Request
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slugify import slugify
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Модели
class User(BaseModel):
    id: int
    name: str
    email: str

class Task(BaseModel):
    id: int
    title: str
    content: str
    priority: int
    user_id: int
    completed: bool
    slug: str

# Хранилища
users = []
tasks = []

# Маршруты для работы с пользователями
@app.post("/user/", response_model=User)
async def create_user(name: str, email: str):
    user_id = users[-1].id + 1 if users else 1
    new_user = User(id=user_id, name=name, email=email)
    users.append(new_user)
    return new_user

@app.get("/users", response_model=List[User])
async def get_users():
    return users

@app.put("/user/{user_id}", response_model=User)
async def update_user(user_id: int, name: str, email: str):
    for user in users:
        if user.id == user_id:
            user.name = name
            user.email = email
            return user
    raise HTTPException(status_code=404, detail="Пользователь не найден")

@app.delete("/user/{user_id}", response_model=User)
async def delete_user(user_id: int = Path(..., description="Введите ID пользователя для удаления")):
    global tasks
    user_to_delete = next((user for user in users if user.id == user_id), None)
    if user_to_delete:
        # Удаляем связанные задачи
        tasks[:] = [task for task in tasks if task.user_id != user_id]
        users.remove(user_to_delete)
        return user_to_delete
    raise HTTPException(status_code=404, detail="Пользователь не найден")

# Маршруты для работы с задачами
@app.post("/task/", response_model=Task)
async def create_task(title: str, content: str, priority: int, user_id: int):
    task_id = tasks[-1].id + 1 if tasks else 1
    slug = slugify(title)  # Генерация slug
    new_task = Task(id=task_id, title=title, content=content, priority=priority, user_id=user_id, completed=False, slug=slug)
    tasks.append(new_task)
    return new_task

@app.get("/tasks", response_class=HTMLResponse)
async def get_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

@app.get("/api/tasks", response_model=List[Task])
async def get_all_tasks():
    return tasks

@app.put("/task/{task_id}", response_model=Task)
async def update_task(task_id: int, title: str, content: str, priority: int, user_id: int, completed: bool):
    for task in tasks:
        if task.id == task_id:
            task.title = title
            task.content = content
            task.priority = priority
            task.user_id = user_id
            task.completed = completed
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")

@app.delete("/task/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")