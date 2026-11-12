import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False, default="Warrior")
    is_active = Column(Boolean, default=True)
    settings_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    reality_reports = relationship("RealityReport", back_populates="user", cascade="all, delete-orphan")
    memory_records = relationship("MemoryRecord", back_populates="user", cascade="all, delete-orphan")
    plan_histories = relationship("PlanHistory", back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="General")  # Career, Fitness, Learning, Discipline
    motivation = Column(Text, nullable=True)
    target_date = Column(String, nullable=True)  # YYYY-MM-DD
    status = Column(String, default="ACTIVE")  # ACTIVE, COMPLETED, ARCHIVED, PAUSED
    progress = Column(Integer, default=0)  # 0 to 100 %
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    plan_histories = relationship("PlanHistory", back_populates="goal", cascade="all, delete-orphan")


class Task(Base):
    """Daily or weekly commitment created by the user or Onboarding/Planner Agents."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(String, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    scheduled_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    priority = Column(String, default="HIGH")  # HIGH, MEDIUM, LOW
    estimated_duration = Column(Integer, default=45)  # minutes
    completion_criteria = Column(Text, nullable=True)
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, PARTIALLY_COMPLETED, MISSED, BLOCKED
    evidence_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    progress_entries = relationship("TaskProgress", back_populates="task", cascade="all, delete-orphan")


class Checkin(Base):
    """Daily accountability checkin session."""
    __tablename__ = "checkins"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    summary = Column(Text, nullable=True)
    overall_status = Column(String, default="PENDING")  # HONEST_SUCCESS, PARTIAL, AVOIDANCE_DETECTED, MISSED
    confrontation_notes = Column(Text, nullable=True)
    raw_transcript = Column(Text, default="[]")  # JSON representation of Q&A
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="checkins")
    progress_entries = relationship("TaskProgress", back_populates="checkin", cascade="all, delete-orphan")


class TaskProgress(Base):
    """Evaluation of an individual task inside a check-in."""
    __tablename__ = "task_progress"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    checkin_id = Column(String, ForeignKey("checkins.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    reported_status = Column(String, nullable=False)  # COMPLETED, PARTIALLY_COMPLETED, MISSED, BLOCKED
    user_notes = Column(Text, nullable=True)
    confrontation_evaluation = Column(Text, nullable=True)
    blocker_reason = Column(Text, nullable=True)
    evidence_submitted = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    checkin = relationship("Checkin", back_populates="progress_entries")
    task = relationship("Task", back_populates="progress_entries")


class PlanHistory(Base):
    """Audit log of schedule adjustments made by Planner Agent."""
    __tablename__ = "plan_histories"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(String, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    previous_plan_json = Column(Text, nullable=False)
    updated_plan_json = Column(Text, nullable=False)
    adaptation_reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="plan_histories")
    goal = relationship("Goal", back_populates="plan_histories")


class RealityReport(Base):
    """Weekly Brutality Reality Report synthesized from deterministic DB data."""
    __tablename__ = "reality_reports"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(String, nullable=False)  # YYYY-MM-DD
    end_date = Column(String, nullable=False)    # YYYY-MM-DD
    total_commitments = Column(Integer, default=0)
    completed_commitments = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    excuse_analysis = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    brutal_truth = Column(Text, nullable=True)
    action_plan = Column(Text, nullable=True)
    report_json = Column(Text, default="{}")
    generated_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="reality_reports")


class MemoryRecord(Base):
    """Long-term memory record storing behavioral patterns, recurring excuses, strengths."""
    __tablename__ = "memory_records"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type = Column(String, nullable=False, index=True)  # EXCUSE_PATTERN, HABIT, STRENGTH, COMMITMENT
    content = Column(Text, nullable=False)
    tags = Column(String, default="")  # comma-delimited
    importance_score = Column(Float, default=0.8)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="memory_records")
