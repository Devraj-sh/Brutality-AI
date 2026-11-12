from fastapi import APIRouter, Depends, status
from app.database import schemas, models
from app.api.deps import get_current_user, get_orchestrator
from app.orchestrator.brutality_orchestrator import BrutalityOrchestrator

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.post("/start", response_model=schemas.OnboardingPlanResponse, status_code=status.HTTP_201_CREATED)
def start_onboarding(
    req: schemas.OnboardingStartRequest,
    user: models.User = Depends(get_current_user),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Agent 1 (Onboarding): Converts high-level goal into structured milestones
    and scheduled daily commitments stored in the database.
    """
    result = orchestrator.run_onboarding(
        user_id=user.id,
        primary_goal=req.primary_goal,
        motivation=req.motivation or "",
        current_level=req.current_level or "Intermediate",
        available_hours=req.available_hours_per_week or 10.0,
        timeframe_days=req.timeframe_days or 30,
        constraints=req.constraints or ""
    )
    return result
