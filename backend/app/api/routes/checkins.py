from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import schemas, models, repositories
from app.api.deps import get_current_user, get_orchestrator
from app.orchestrator.brutality_orchestrator import BrutalityOrchestrator

router = APIRouter(prefix="/checkins", tags=["Daily Check-ins"])

@router.get("/today", response_model=Dict[str, Any])
def get_today_checkin(
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    user: models.User = Depends(get_current_user),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Agent 2 (Check-in Agent): Retrieves today's commitments and generates
    personalized accountability questions.
    """
    return orchestrator.get_daily_checkin_context(user_id=user.id, date_str=date)

@router.post("/submit", response_model=schemas.CheckinEvaluationResponse)
def submit_checkin(
    req: schemas.CheckinSubmitRequest,
    user: models.User = Depends(get_current_user),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Agent 3 (Confront Agent) + Agent 4 (Planner Agent):
    Evaluates promised vs delivered work, classifies outcome, confronts excuses,
    and adapts future schedule if commitments were missed.
    """
    updates = [u.model_dump() for u in req.task_updates]
    result = orchestrator.process_checkin_submission(
        user_id=user.id,
        date_str=req.date,
        task_updates=updates,
        overall_reflection=req.overall_reflection or ""
    )
    return result

@router.get("/history", response_model=List[Dict[str, Any]])
def get_checkin_history(
    limit: int = Query(14, ge=1, le=60),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.CheckinRepository(db)
    checkins = repo.get_history(user.id, limit=limit)
    return [
        {
            "id": c.id,
            "date": c.date,
            "overall_status": c.overall_status,
            "summary": c.summary,
            "confrontation_notes": c.confrontation_notes,
            "created_at": c.created_at
        }
        for c in checkins
    ]
