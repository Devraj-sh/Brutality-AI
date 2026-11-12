from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from app.database import models
from datetime import datetime, timezone

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email.lower()).first()

    def create(self, email: str, hashed_password: str, full_name: str) -> models.User:
        user = models.User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: str) -> List[models.Goal]:
        return self.db.query(models.Goal).filter(models.Goal.user_id == user_id).order_by(desc(models.Goal.created_at)).all()

    def get_by_id(self, goal_id: str, user_id: str) -> Optional[models.Goal]:
        return self.db.query(models.Goal).filter(
            models.Goal.id == goal_id,
            models.Goal.user_id == user_id
        ).first()

    def create(self, user_id: str, title: str, description: str = "", category: str = "General", motivation: str = "", target_date: str = "", status: str = "ACTIVE") -> models.Goal:
        goal = models.Goal(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            motivation=motivation,
            target_date=target_date,
            status=status
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update(self, goal: models.Goal, **kwargs) -> models.Goal:
        for key, value in kwargs.items():
            if value is not None and hasattr(goal, key):
                setattr(goal, key, value)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: models.Goal) -> None:
        self.db.delete(goal)
        self.db.commit()


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: str, scheduled_date: Optional[str] = None, goal_id: Optional[str] = None, status: Optional[str] = None) -> List[models.Task]:
        query = self.db.query(models.Task).filter(models.Task.user_id == user_id)
        if scheduled_date:
            query = query.filter(models.Task.scheduled_date == scheduled_date)
        if goal_id:
            query = query.filter(models.Task.goal_id == goal_id)
        if status:
            query = query.filter(models.Task.status == status)
        return query.order_by(models.Task.scheduled_date.asc(), models.Task.created_at.asc()).all()

    def get_by_id(self, task_id: str, user_id: str) -> Optional[models.Task]:
        return self.db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == user_id
        ).first()

    def create(self, user_id: str, title: str, scheduled_date: str, goal_id: Optional[str] = None, description: str = "", priority: str = "HIGH", estimated_duration: int = 45, completion_criteria: str = "", status: str = "PENDING") -> models.Task:
        task = models.Task(
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            priority=priority,
            estimated_duration=estimated_duration,
            completion_criteria=completion_criteria,
            status=status
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: models.Task, **kwargs) -> models.Task:
        for key, value in kwargs.items():
            if value is not None and hasattr(task, key):
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: models.Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def get_stats(self, user_id: str) -> Dict[str, Any]:
        tasks = self.db.query(models.Task).filter(models.Task.user_id == user_id).all()
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "COMPLETED")
        missed = sum(1 for t in tasks if t.status in ["MISSED", "BLOCKED"])
        rate = round((completed / total * 100), 1) if total > 0 else 0.0
        
        # Streak calculation (consecutive days with at least 1 completed task)
        completed_dates = sorted(list(set(t.scheduled_date for t in tasks if t.status == "COMPLETED")))
        streak = len(completed_dates) # approximate streak
        longest_streak = max(streak, 1) if streak > 0 else 0
        consistency_score = int(rate)

        return {
            "total_commitments": total,
            "completed_commitments": completed,
            "missed_commitments": missed,
            "completion_rate": rate,
            "consistency_score": consistency_score,
            "current_streak": streak,
            "longest_streak": longest_streak
        }


class CheckinRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_date(self, user_id: str, date: str) -> Optional[models.Checkin]:
        return self.db.query(models.Checkin).filter(
            models.Checkin.user_id == user_id,
            models.Checkin.date == date
        ).first()

    def create(self, user_id: str, date: str, summary: str = "", overall_status: str = "PENDING", confrontation_notes: str = "", raw_transcript: str = "[]") -> models.Checkin:
        checkin = models.Checkin(
            user_id=user_id,
            date=date,
            summary=summary,
            overall_status=overall_status,
            confrontation_notes=confrontation_notes,
            raw_transcript=raw_transcript
        )
        self.db.add(checkin)
        self.db.commit()
        self.db.refresh(checkin)
        return checkin

    def add_progress(self, checkin_id: str, task_id: str, reported_status: str, user_notes: str = "", confrontation_evaluation: str = "", blocker_reason: str = "", evidence_submitted: str = "", confidence_score: float = 1.0) -> models.TaskProgress:
        prog = models.TaskProgress(
            checkin_id=checkin_id,
            task_id=task_id,
            reported_status=reported_status,
            user_notes=user_notes,
            confrontation_evaluation=confrontation_evaluation,
            blocker_reason=blocker_reason,
            evidence_submitted=evidence_submitted,
            confidence_score=confidence_score
        )
        self.db.add(prog)
        self.db.commit()
        self.db.refresh(prog)
        return prog

    def get_history(self, user_id: str, limit: int = 14) -> List[models.Checkin]:
        return self.db.query(models.Checkin).filter(
            models.Checkin.user_id == user_id
        ).order_by(desc(models.Checkin.date)).limit(limit).all()


class RealityReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, start_date: str, end_date: str, total_commitments: int, completed_commitments: int, completion_rate: float, excuse_analysis: str, strengths: str, brutal_truth: str, action_plan: str, report_json: str = "{}") -> models.RealityReport:
        rep = models.RealityReport(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            total_commitments=total_commitments,
            completed_commitments=completed_commitments,
            completion_rate=completion_rate,
            excuse_analysis=excuse_analysis,
            strengths=strengths,
            brutal_truth=brutal_truth,
            action_plan=action_plan,
            report_json=report_json
        )
        self.db.add(rep)
        self.db.commit()
        self.db.refresh(rep)
        return rep

    def get_latest(self, user_id: str) -> Optional[models.RealityReport]:
        return self.db.query(models.RealityReport).filter(
            models.RealityReport.user_id == user_id
        ).order_by(desc(models.RealityReport.generated_at)).first()

    def get_all(self, user_id: str) -> List[models.RealityReport]:
        return self.db.query(models.RealityReport).filter(
            models.RealityReport.user_id == user_id
        ).order_by(desc(models.RealityReport.generated_at)).all()


class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, user_id: str, memory_type: str, content: str, tags: str = "", importance_score: float = 0.8) -> models.MemoryRecord:
        record = models.MemoryRecord(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            tags=tags,
            importance_score=importance_score
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_recent(self, user_id: str, limit: int = 10, memory_type: Optional[str] = None) -> List[models.MemoryRecord]:
        query = self.db.query(models.MemoryRecord).filter(models.MemoryRecord.user_id == user_id)
        if memory_type:
            query = query.filter(models.MemoryRecord.memory_type == memory_type)
        return query.order_by(desc(models.MemoryRecord.created_at)).limit(limit).all()


class PlanHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: str, goal_id: Optional[str], previous_plan_json: str, updated_plan_json: str, adaptation_reason: str) -> models.PlanHistory:
        hist = models.PlanHistory(
            user_id=user_id,
            goal_id=goal_id,
            previous_plan_json=previous_plan_json,
            updated_plan_json=updated_plan_json,
            adaptation_reason=adaptation_reason
        )
        self.db.add(hist)
        self.db.commit()
        self.db.refresh(hist)
        return hist
