from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.database import repositories, schemas, models
from app.api.deps import get_current_user

router = APIRouter(prefix="/memory", tags=["Memory Agent"])

@router.get("/insights", response_model=List[schemas.MemoryRecordResponse])
def get_memory_insights(
    memory_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.MemoryRepository(db)
    return repo.get_recent(user_id=user.id, limit=limit, memory_type=memory_type)

@router.post("/records", response_model=schemas.MemoryRecordResponse, status_code=status.HTTP_201_CREATED)
def create_memory_record(
    req: schemas.MemoryRecordCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.MemoryRepository(db)
    return repo.add(
        user_id=user.id,
        memory_type=req.memory_type,
        content=req.content,
        tags=req.tags or "",
        importance_score=req.importance_score
    )
