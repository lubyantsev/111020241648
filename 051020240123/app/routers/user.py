from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import select, insert, update
from typing import List, Annotated

router = APIRouter(prefix="/user", tags=["user"])

# Retrieve all users
@router.get("/", response_model=List[User])
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()
    return users

# Retrieve a user by ID
@router.get("/{user_id}", response_model=User)
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user

# Create a new user
@router.post("/create", response_model=User)
async def create_user(new_user: CreateUser, db: Session = Depends(get_db)):
    db.execute(insert(User).values(new_user.dict(exclude_unset=True)))
    db.commit()
    return {"message": "User created successfully"}

# Update an existing user
@router.put("/update/{user_id}", response_model=User)
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(user.dict()))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

# Delete a user by ID
@router.delete("/delete/{user_id}", response_model=User)
async def delete_user(user_id: int = Path(..., description="Enter the user ID to delete"), db: Session = Depends(get_db)):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete:
        # Delete associated tasks
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.delete(user_to_delete)
        db.commit()
        return user_to_delete
    raise HTTPException(status_code=404, detail="User was not found")

# Retrieve tasks associated with a user
@router.get("/{user_id}/tasks", response_model=List[Task])
async def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user_tasks = db.query(Task).filter(Task.user_id == user_id).all()
    if not user_tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this user")
    return user_tasks