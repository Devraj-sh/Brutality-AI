import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.database import models, repositories
from app.memory.memory_service import MemoryService
from app.agents.onboarding_agent import OnboardingAgent
from app.agents.checkin_agent import CheckinAgent
from app.agents.confront_agent import ConfrontAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.reality_agent import RealityAgent
from app.agents.memory_agent import MemoryAgent
from app.services.ai_service import get_ai_service

class BrutalityOrchestrator:
    """
    Central Multi-Agent Orchestrator for BRUTALITY AI.
    Coordinates agents, executes business logic, maintains database integrity,
    and isolates user state.
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai = get_ai_service()
        self.memory = MemoryService(db)

        # Repositories
        self.user_repo = repositories.UserRepository(db)
        self.goal_repo = repositories.GoalRepository(db)
        self.task_repo = repositories.TaskRepository(db)
        self.checkin_repo = repositories.CheckinRepository(db)
        self.report_repo = repositories.RealityReportRepository(db)
        self.plan_history_repo = repositories.PlanHistoryRepository(db)

        # Specialized Agents
        self.onboarding_agent = OnboardingAgent(self.ai)
        self.checkin_agent = CheckinAgent(self.ai)
        self.confront_agent = ConfrontAgent(self.ai)
        self.planner_agent = PlannerAgent(self.ai)
        self.reality_agent = RealityAgent(self.ai)
        self.memory_agent = MemoryAgent(self.ai)

    # -------------------------------------------------------------
    # 1. Onboarding Flow
    # -------------------------------------------------------------
    def run_onboarding(
        self,
        user_id: str,
        primary_goal: str,
        motivation: str = "",
        current_level: str = "Intermediate",
        available_hours: float = 10.0,
        timeframe_days: int = 30,
        constraints: str = ""
    ) -> Dict[str, Any]:
        """Runs the Onboarding Agent to create a Goal and scheduled Commitments."""
        # Calculate target date
        target_date = (datetime.now(timezone.utc).date() + timedelta(days=timeframe_days)).strftime("%Y-%m-%d")

        # 1. Create the Goal in DB
        goal = self.goal_repo.create(
            user_id=user_id,
            title=primary_goal,
            description=f"Generated via Brutality AI Onboarding. Level: {current_level}. Allocation: {available_hours}h/wk.",
            category="Core Discipline",
            motivation=motivation,
            target_date=target_date,
            status="ACTIVE"
        )

        # 2. Agent generates the plan
        plan = self.onboarding_agent.generate_plan(
            goal_title=primary_goal,
            motivation=motivation,
            current_level=current_level,
            available_hours=available_hours,
            timeframe_days=timeframe_days,
            constraints=constraints
        )

        # 3. Persist Commitments as Tasks in DB
        created_tasks = []
        for c in plan.get("commitments", []):
            task = self.task_repo.create(
                user_id=user_id,
                goal_id=goal.id,
                title=c.get("title", "Commitment"),
                description=c.get("description", ""),
                scheduled_date=c.get("scheduled_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                priority=c.get("priority", "HIGH"),
                estimated_duration=int(c.get("estimated_duration", 45)),
                completion_criteria=c.get("completion_criteria", "Deliver requested output"),
                status="PENDING"
            )
            created_tasks.append(task)

        # 4. Log initial memory baseline
        self.memory.record_interaction_memory(
            user_id=user_id,
            memory_type="GOAL_ESTABLISHED",
            content=f"User committed to primary goal '{primary_goal}' with {len(created_tasks)} initial scheduled tasks.",
            tags=["goal", "onboarding"],
            importance_score=1.0
        )

        return {
            "goal": goal,
            "commitments_created": created_tasks,
            "strategy_overview": plan.get("strategy_overview", "Disciplined daily execution framework."),
            "weekly_breakdown": plan.get("weekly_breakdown", [])
        }

    # -------------------------------------------------------------
    # 2. Daily Check-in & Confrontation Flow
    # -------------------------------------------------------------
    def get_daily_checkin_context(self, user_id: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Prepares today's checkin questionnaire using CheckinAgent."""
        today = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tasks = self.task_repo.get_all(user_id=user_id, scheduled_date=today)
        user = self.user_repo.get_by_id(user_id)
        user_name = user.full_name if user else "Warrior"

        task_dicts = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "estimated_duration": t.estimated_duration,
                "completion_criteria": t.completion_criteria,
                "status": t.status
            }
            for t in tasks
        ]

        return self.checkin_agent.generate_checkin_prompt(tasks=task_dicts, user_name=user_name)

    def process_checkin_submission(
        self,
        user_id: str,
        date_str: str,
        task_updates: List[Dict[str, Any]],
        overall_reflection: str = ""
    ) -> Dict[str, Any]:
        """
        Coordinates Confront Agent evaluation, updates DB task statuses,
        records excuse patterns, and invokes Planner Agent if commitments were missed.
        """
        user_mem_context = self.memory.get_user_context(user_id=user_id)
        task_evaluations = []
        missed_tasks_for_planner = []
        any_avoidance = False
        all_completed = True

        # Create or update Checkin session in DB
        checkin = self.checkin_repo.create(
            user_id=user_id,
            date=date_str,
            summary=overall_reflection,
            overall_status="PROCESSING",
            raw_transcript=json.dumps(task_updates)
        )

        for update in task_updates:
            task_id = update.get("task_id")
            reported_status = update.get("reported_status", "MISSED").upper()
            notes = update.get("user_notes", "")
            evidence_url = update.get("evidence_url")

            task = self.task_repo.get_by_id(task_id, user_id=user_id)
            if not task:
                continue

            # Confront Agent evaluates this specific update
            evaluation = self.confront_agent.evaluate_task_update(
                task_title=task.title,
                completion_criteria=task.completion_criteria or "Deliver required output",
                reported_status=reported_status,
                user_notes=notes,
                user_memory_context=user_mem_context
            )

            final_status = evaluation.get("status", reported_status)
            if final_status != "COMPLETED":
                all_completed = False
                missed_tasks_for_planner.append({
                    "id": task.id,
                    "title": task.title,
                    "criteria": task.completion_criteria
                })

            if evaluation.get("avoidance_detected") or evaluation.get("is_vague"):
                any_avoidance = True
                self.memory.detect_and_store_excuses(user_id, task.title, notes)

            # Update Task in DB
            self.task_repo.update(
                task,
                status=final_status,
                evidence_url=evidence_url,
                notes=notes
            )

            # Record TaskProgress in DB
            self.checkin_repo.add_progress(
                checkin_id=checkin.id,
                task_id=task.id,
                reported_status=final_status,
                user_notes=notes,
                confrontation_evaluation=evaluation.get("evaluation_text", ""),
                blocker_reason=notes if final_status in ["MISSED", "BLOCKED"] else "",
                evidence_submitted=evidence_url or "",
                confidence_score=evaluation.get("confidence_level", 0.95)
            )

            task_evaluations.append({
                "task_id": task.id,
                "status": final_status,
                "evaluation_text": evaluation.get("evaluation_text", ""),
                "is_vague": evaluation.get("is_vague", False),
                "avoidance_detected": evaluation.get("avoidance_detected", False),
                "evidence_requested": evaluation.get("evidence_requested", False),
                "confidence_level": evaluation.get("confidence_level", 0.95),
                "recommended_action": evaluation.get("recommended_action", "Keep executing.")
            })

        # Determine overall status
        if all_completed and len(task_evaluations) > 0:
            overall_status = "HONEST_SUCCESS"
            brutal_feedback = "Flawless execution delivered today. The standard was upheld without compromise."
        elif any_avoidance:
            overall_status = "AVOIDANCE_DETECTED"
            brutal_feedback = "Rationalizations and excuses detected. You compromised on your stated commitments today."
        elif not all_completed:
            overall_status = "PARTIAL"
            brutal_feedback = "Partial delivery. Some targets met, but the gap remains unclosed."
        else:
            overall_status = "PENDING"
            brutal_feedback = "Check-in logged."

        checkin.overall_status = overall_status
        checkin.confrontation_notes = brutal_feedback
        self.db.commit()

        # Invoke Planner Agent if tasks were missed
        planner_applied = False
        adjusted_count = 0
        if missed_tasks_for_planner:
            upcoming = self.task_repo.get_all(user_id=user_id, status="PENDING")
            upcoming_dicts = [{"id": u.id, "title": u.title, "scheduled_date": u.scheduled_date} for u in upcoming]
            
            plan_adjustment = self.planner_agent.adapt_plan(
                missed_tasks=missed_tasks_for_planner,
                upcoming_tasks=upcoming_dicts
            )

            # Apply adjustments to DB tasks
            for idx, adj in enumerate(plan_adjustment.get("adjustments", [])):
                t_id = adj.get("task_id")
                target_task = self.task_repo.get_by_id(t_id, user_id=user_id) if t_id else None
                if not target_task and idx < len(missed_tasks_for_planner):
                    target_task = self.task_repo.get_by_id(missed_tasks_for_planner[idx]["id"], user_id=user_id)

                if target_task:
                    new_date = adj.get("new_scheduled_date")
                    if not new_date or new_date == "next_day":
                        new_date = (datetime.now(timezone.utc).date() + timedelta(days=1)).strftime("%Y-%m-%d")
                    self.task_repo.update(target_task, scheduled_date=new_date, status="PENDING")
                    adjusted_count += 1


            if adjusted_count > 0:
                planner_applied = True
                self.plan_history_repo.log(
                    user_id=user_id,
                    goal_id=None,
                    previous_plan_json=json.dumps(missed_tasks_for_planner),
                    updated_plan_json=json.dumps(plan_adjustment),
                    adaptation_reason=plan_adjustment.get("explanation", "Rescheduled missed commitments.")
                )

        return {
            "checkin_id": checkin.id,
            "date": date_str,
            "overall_status": overall_status,
            "brutal_feedback": brutal_feedback,
            "task_evaluations": task_evaluations,
            "planner_applied": planner_applied,
            "adjusted_tasks_count": adjusted_count
        }

    # -------------------------------------------------------------
    # 3. Reality Report Flow (Agent 5)
    # -------------------------------------------------------------
    def generate_weekly_reality_report(self, user_id: str) -> models.RealityReport:
        """Calculates deterministic DB stats and asks RealityAgent to generate report."""
        stats = self.task_repo.get_stats(user_id)
        now = datetime.now(timezone.utc).date()
        start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")

        # Retrieve recent goals
        goals = self.goal_repo.get_all(user_id)
        goals_summary = ", ".join([g.title for g in goals[:3]]) if goals else "None"

        # Retrieve recent excuses
        recent_memories = self.memory.repo.get_recent(user_id=user_id, memory_type="EXCUSE_PATTERN", limit=5)
        excuses = [m.content for m in recent_memories]

        report_data = self.reality_agent.generate_reality_report(
            total_tasks=stats["total_commitments"],
            completed_tasks=stats["completed_commitments"],
            missed_tasks=stats["missed_commitments"],
            completion_rate=stats["completion_rate"],
            recent_excuses=excuses,
            goals_summary=goals_summary
        )

        reality_report = self.report_repo.create(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            total_commitments=stats["total_commitments"],
            completed_commitments=stats["completed_commitments"],
            completion_rate=stats["completion_rate"],
            excuse_analysis=report_data.get("excuse_analysis", ""),
            strengths=report_data.get("strengths", ""),
            brutal_truth=report_data.get("brutal_truth", ""),
            action_plan=report_data.get("action_plan", ""),
            report_json=json.dumps(report_data)
        )

        return reality_report

    # -------------------------------------------------------------
    # 4. Interactive Chat Flow
    # -------------------------------------------------------------
    def chat_message(self, user_id: str, message: str, goal_id: Optional[str] = None) -> Dict[str, Any]:
        """Routes chat interaction with memory context and Brutality persona."""
        mem_context = self.memory.get_user_context(user_id=user_id, query_hint=message)
        system_prompt = (
            "You are BRUTALITY AI. "
            "You are direct, disciplined, honest, constructive, and uncompromising. "
            "Help the user execute their goals. Call out avoidance and demand clarity without insulting them.\n"
            f"User memory history:\n{mem_context}"
        )
        reply = self.ai.generate_text(system_prompt, message)

        suggestions = [
            "What should I do right now?",
            "Confront my recent progress",
            "Generate my Reality Report"
        ]

        return {
            "reply": reply,
            "agent_name": "BrutalityOrchestrator",
            "intent": "COACHING",
            "suggestions": suggestions,
            "metadata": {"has_memory_context": bool(mem_context)}
        }
