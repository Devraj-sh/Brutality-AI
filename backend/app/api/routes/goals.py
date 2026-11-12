from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import repositories, schemas, models
from app.api.deps import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("", response_model=List[schemas.GoalResponse])
def get_goals(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.GoalRepository(db)
    return repo.get_all(user.id)

@router.post("", response_model=schemas.GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    req: schemas.GoalCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.GoalRepository(db)
    return repo.create(
        user_id=user.id,
        title=req.title,
        description=req.description or "",
        category=req.category or "General",
        motivation=req.motivation or "",
        target_date=req.target_date or "",
        status=req.status or "ACTIVE"
    )

@router.get("/{goal_id}", response_model=schemas.GoalWithTasks)
def get_goal(
    goal_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.GoalRepository(db)
    goal = repo.get_by_id(goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return goal

@router.put("/{goal_id}", response_model=schemas.GoalResponse)
def update_goal(
    goal_id: str,
    req: schemas.GoalUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.GoalRepository(db)
    goal = repo.get_by_id(goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return repo.update(goal, **req.model_dump(exclude_unset=True))

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.GoalRepository(db)
    goal = repo.get_by_id(goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    repo.delete(goal)
    return None
