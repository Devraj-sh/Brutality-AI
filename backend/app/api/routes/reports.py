from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import repositories, schemas, models
from app.api.deps import get_current_user, get_orchestrator
from app.orchestrator.brutality_orchestrator import BrutalityOrchestrator

router = APIRouter(prefix="/reports", tags=["Reality Reports"])

@router.get("/reality", response_model=schemas.RealityReportResponse)
def get_latest_reality_report(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Agent 5 (Reality Agent): Returns the user's latest Reality Report.
    If none exists yet, automatically synthesizes one from database statistics.
    """
    repo = repositories.RealityReportRepository(db)
    report = repo.get_latest(user.id)
    if not report:
        report = orchestrator.generate_weekly_reality_report(user.id)
    return report

@router.post("/reality/generate", response_model=schemas.RealityReportResponse, status_code=status.HTTP_201_CREATED)
def generate_reality_report(
    user: models.User = Depends(get_current_user),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Agent 5 (Reality Agent): Forces generation of a new weekly Reality Report
    based strictly on deterministic DB completion metrics.
    """
    return orchestrator.generate_weekly_reality_report(user.id)

@router.get("/history", response_model=List[schemas.RealityReportResponse])
def get_report_history(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = repositories.RealityReportRepository(db)
    return repo.get_all(user.id)
