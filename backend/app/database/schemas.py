from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(default="Warrior")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Task / Commitment Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_date: str = Field(..., description="Format YYYY-MM-DD")
    priority: str = Field(default="HIGH", description="HIGH, MEDIUM, LOW")
    estimated_duration: int = Field(default=45, description="Minutes")
    completion_criteria: Optional[str] = None
    status: str = Field(default="PENDING", description="PENDING, COMPLETED, PARTIALLY_COMPLETED, MISSED, BLOCKED")
    evidence_url: Optional[str] = None
    notes: Optional[str] = None

class TaskCreate(TaskBase):
    goal_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    priority: Optional[str] = None
    estimated_duration: Optional[int] = None
    completion_criteria: Optional[str] = None
    status: Optional[str] = None
    evidence_url: Optional[str] = None
    notes: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    user_id: str
    goal_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Goal Schemas ---
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "General"
    motivation: Optional[str] = None
    target_date: Optional[str] = None
    status: str = "ACTIVE"

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    motivation: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None

class GoalResponse(GoalBase):
    id: str
    user_id: str
    progress: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GoalWithTasks(GoalResponse):
    tasks: List[TaskResponse] = []

# --- Check-in & Confrontation Schemas ---
class TaskCheckinItem(BaseModel):
    task_id: str
    reported_status: str = Field(..., description="COMPLETED, PARTIALLY_COMPLETED, MISSED, BLOCKED")
    user_notes: Optional[str] = None
    evidence_url: Optional[str] = None

class CheckinSubmitRequest(BaseModel):
    date: str
    task_updates: List[TaskCheckinItem]
    overall_reflection: Optional[str] = None

class ConfrontEvaluation(BaseModel):
    task_id: str
    status: str
    evaluation_text: str
    is_vague: bool = False
    avoidance_detected: bool = False
    evidence_requested: bool = False
    confidence_level: float = 1.0
    recommended_action: str

class CheckinEvaluationResponse(BaseModel):
    checkin_id: str
    date: str
    overall_status: str
    brutal_feedback: str
    task_evaluations: List[ConfrontEvaluation]
    planner_applied: bool
    adjusted_tasks_count: int

# --- Onboarding Schemas ---
class OnboardingStartRequest(BaseModel):
    primary_goal: str
    motivation: Optional[str] = None
    current_level: Optional[str] = "Intermediate"
    available_hours_per_week: Optional[float] = 10.0
    timeframe_days: Optional[int] = 30
    constraints: Optional[str] = None

class OnboardingPlanResponse(BaseModel):
    goal: GoalResponse
    commitments_created: List[TaskResponse]
    strategy_overview: str
    weekly_breakdown: List[str]

# --- Planner Schemas ---
class PlanAdjustmentRequest(BaseModel):
    goal_id: Optional[str] = None
    force_reschedule: bool = False

class PlanAdjustmentResponse(BaseModel):
    rescheduled_tasks: List[TaskResponse]
    explanation: str
    preserved_completed_count: int

# --- Reality Report & Stats Schemas ---
class PerformanceStats(BaseModel):
    total_commitments: int
    completed_commitments: int
    missed_commitments: int
    completion_rate: float
    consistency_score: int
    current_streak: int
    longest_streak: int
    active_goals_count: int

class RealityReportResponse(BaseModel):
    id: str
    user_id: str
    start_date: str
    end_date: str
    total_commitments: int
    completed_commitments: int
    completion_rate: float
    excuse_analysis: str
    strengths: str
    brutal_truth: str
    action_plan: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Dashboard Schemas ---
class ActivityFeedItem(BaseModel):
    id: str
    type: str  # CHECKIN, GOAL_CREATED, TASK_COMPLETED, CONFRONTATION, REPORT_GENERATED
    title: str
    timestamp: str
    description: Optional[str] = None

class DashboardSummaryResponse(BaseModel):
    stats: PerformanceStats
    today_commitments: List[TaskResponse]
    recent_activity: List[ActivityFeedItem]
    accountability_status: str
    quote: str

# --- Memory Schemas ---
class MemoryRecordCreate(BaseModel):
    memory_type: str
    content: str
    tags: Optional[str] = ""
    importance_score: float = 0.8

class MemoryRecordResponse(BaseModel):
    id: str
    user_id: str
    memory_type: str
    content: str
    tags: str
    importance_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Chat Schemas ---
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    goal_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    reply: str
    agent_name: str
    intent: str
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}
