from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.database import get_db
from app.database import repositories, schemas, models
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas.PerformanceStats)
def get_stats(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_repo = repositories.TaskRepository(db)
    goal_repo = repositories.GoalRepository(db)
    
    stats = task_repo.get_stats(user.id)
    active_goals = len([g for g in goal_repo.get_all(user.id) if g.status == "ACTIVE"])
    stats["active_goals_count"] = active_goals
    return stats

@router.get("/summary", response_model=schemas.DashboardSummaryResponse)
def get_dashboard_summary(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_repo = repositories.TaskRepository(db)
    goal_repo = repositories.GoalRepository(db)
    checkin_repo = repositories.CheckinRepository(db)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_tasks = task_repo.get_all(user_id=user.id, scheduled_date=today)
    
    stats_dict = task_repo.get_stats(user.id)
    stats_dict["active_goals_count"] = len([g for g in goal_repo.get_all(user.id) if g.status == "ACTIVE"])

    recent_checkins = checkin_repo.get_history(user.id, limit=3)
    activity = []
    for c in recent_checkins:
        activity.append(schemas.ActivityFeedItem(
            id=c.id,
            type="CHECKIN",
            title=f"Check-in: {c.overall_status.replace('_', ' ').title()}",
            timestamp=c.created_at.strftime("%b %d, %H:%M"),
            description=c.confrontation_notes or c.summary
        ))

    rate = stats_dict["completion_rate"]
    if rate >= 85:
        status_text = "Dominant Execution"
    elif rate >= 65:
        status_text = "Disciplined but Inconsistent"
    elif rate >= 40:
        status_text = "Vulnerable to Distraction"
    else:
        status_text = "Critical Drift"

    return schemas.DashboardSummaryResponse(
        stats=schemas.PerformanceStats(**stats_dict),
        today_commitments=[schemas.TaskResponse.model_validate(t) for t in today_tasks],
        recent_activity=activity,
        accountability_status=status_text,
        quote="Discipline is choosing between what you want now and what you want most."
    )
