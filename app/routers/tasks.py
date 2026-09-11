from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.models.users import User

# Import our DB session helper, model, and schemas
from app.database import get_db
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskResponse, TaskUpdate
from app.routers.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# 1. Create a task in the Database
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_user = db.query(User).filter(User.id == current_user.id).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {current_user.id} does not exist.")

    new_task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        owner_id=current_user.id,
    )

    db.add(new_task)  # Stage the new record
    db.commit()  # Save changes permanently to tasksphere.db file
    db.refresh(new_task)  # Load generated fields (like 'id') back into new_task

    return new_task

# 2. Get all tasks from the Database
@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=0, le=100),
    completed: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    if completed is not None:
        query = query.filter(Task.is_completed == completed)


    tasks = query.offset(skip).limit(limit).all()
    return tasks

# 3. Get a single task by ID
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} was not found.",
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to view this task.",
        )
    return task

# 4. Delete a task from the Database
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} was not found.",
        )
    if Task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to delete this task.",
        )

    db.delete(task)
    db.commit()  # Save deletion to disk
    return {"message": "Task deleted successfully"}

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task_query = db.query(Task).filter(Task.id == task_id)
    task = task_query.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} was not found.")

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Not authorized to update this task"
        )

    update_data = payload.model_dump(exclude_unset=True)

    task_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(task)

    return task
    