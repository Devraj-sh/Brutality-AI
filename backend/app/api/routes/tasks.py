from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.database import repositories, schemas, models
from app.api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks / Commitments"])

@router.get("", response_model=List[schemas.TaskResponse])
def get_tasks(
    scheduled_date: Optional[str] = Query(None, description="Format YYYY-MM-DD"),
    goal_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.TaskRepository(db)
    return repo.get_all(user_id=user.id, scheduled_date=scheduled_date, goal_id=goal_id, status=status)

@router.post("", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    req: schemas.TaskCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.TaskRepository(db)
    return repo.create(
        user_id=user.id,
        goal_id=req.goal_id,
        title=req.title,
        description=req.description or "",
        scheduled_date=req.scheduled_date,
        priority=req.priority or "HIGH",
        estimated_duration=req.estimated_duration or 45,
        completion_criteria=req.completion_criteria or "",
        status=req.status or "PENDING"
    )

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.TaskRepository(db)
    task = repo.get_by_id(task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: str,
    req: schemas.TaskUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.TaskRepository(db)
    task = repo.get_by_id(task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return repo.update(task, **req.model_dump(exclude_unset=True))

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.TaskRepository(db)
    task = repo.get_by_id(task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    repo.delete(task)
    return None
