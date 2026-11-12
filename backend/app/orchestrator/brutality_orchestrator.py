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
    # 4. Interactive Multi-Agent Chat Routing
    # -------------------------------------------------------------
    def chat_message(self, user_id: str, message: str, goal_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Dynamically routes user messages to the appropriate specialized AI agent
        (Onboarding, Check-in, Confront, Planner, Reality, Memory) with real DB data.
        """
        msg_clean = message.strip()
        lower = msg_clean.lower()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. WHAT TO DO NOW / TASKS INTENT
        if any(w in lower for w in ["what should i do", "what do i do", "what's next", "whats next", "tasks", "my task", "show today", "schedule", "to-do", "todo", "right now"]):
            today_tasks = self.task_repo.get_all(user_id=user_id, scheduled_date=today)
            pending = [t for t in today_tasks if t.status == "PENDING"]
            completed = [t for t in today_tasks if t.status == "COMPLETED"]
            missed = [t for t in today_tasks if t.status in ["MISSED", "BLOCKED"]]

            if pending:
                next_task = pending[0]
                task_lines = "\n".join([f"• [{t.priority}] **{t.title}** (~{t.estimated_duration}m) — Criteria: {t.completion_criteria or 'Deliver required output'}" for t in pending])
                reply = (
                    f"You have **{len(pending)} pending commitment{'s' if len(pending) > 1 else ''}** for today:\n\n"
                    f"{task_lines}\n\n"
                    f"👉 **Immediate Order:** Attack **{next_task.title}** right now.\n"
                    f"Target duration: {next_task.estimated_duration} minutes. No phone. No browsing. Log your execution when done."
                )
                suggestions = [
                    f"Mark '{next_task.title}' as Completed",
                    "I am blocked on this task",
                    "Confront my recent progress"
                ]
            elif completed:
                reply = (
                    f"You have already crushed all **{len(completed)} scheduled commitments** for today!\n\n"
                    f"{chr(10).join([f'✓ {t.title}' for t in completed])}\n\n"
                    "Execution standard upheld. Rest deliberately or lock in tomorrow's commitments."
                )
                suggestions = ["Review my progress", "Generate my Reality Report", "Plan tomorrow's commitments"]
            else:
                reply = (
                    "Zero commitments are currently scheduled for today on your board. That is an accountability gap.\n\n"
                    "Without a daily commitment, drift is guaranteed. What is your primary objective today? State it and I will lock it in."
                )
                suggestions = ["Solve 2 LeetCode problems", "Complete 45 min workout", "Ship core backend feature"]

            return {
                "reply": reply,
                "agent_name": "Check-in Agent",
                "intent": "TASKS",
                "suggestions": suggestions,
                "metadata": {"pending_count": len(pending), "completed_count": len(completed)}
            }

        # 2. CONFRONT / REVIEW PROGRESS INTENT
        if any(w in lower for w in ["progress", "review my progress", "confront my recent progress", "how am i doing", "streak", "consistency", "score"]):
            stats = self.task_repo.get_stats(user_id)
            rate = stats["completion_rate"]
            streak = stats["current_streak"]

            if rate >= 80:
                tone = "You are delivering with high discipline. The standard is being upheld, but complacency is the enemy. Maintain the streak."
            elif rate >= 50:
                tone = "You are inconsistent. Half of your commitments are being compromised by excuses. Turn that 50% into non-negotiable delivery."
            else:
                tone = "Critical discipline failure. You are promising much more than you actually deliver. Close the gap immediately."

            reply = (
                f"**ACCOUNTABILITY AUDIT — VERIFIED METRICS**\n\n"
                f"• **Completion Rate:** {rate}%\n"
                f"• **Consistency Score:** {stats['consistency_score']}/100\n"
                f"• **Current Streak:** {streak} days\n"
                f"• **Total Deliverables:** {stats['total_commitments']} ({stats['completed_commitments']} Completed, {stats['missed_commitments']} Missed)\n\n"
                f"{tone}"
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "PROGRESS",
                "suggestions": ["What should I do right now?", "Generate my Reality Report", "Analyze my excuses"],
                "metadata": stats
            }

        # 3. REALITY REPORT INTENT
        if any(w in lower for w in ["reality report", "generate report", "generate reality", "weekly report"]):
            report = self.generate_weekly_reality_report(user_id)
            reply = (
                f"**WEEKLY BRUTALITY REALITY REPORT**\n\n"
                f"**The Brutal Truth:**\n{report.brutal_truth}\n\n"
                f"**Excuse Diagnostic:**\n{report.excuse_analysis}\n\n"
                f"**Verified Strengths:**\n{report.strengths}\n\n"
                f"**Operational Action Protocol:**\n{report.action_plan}\n\n"
                f"• Verified Delivery Rate: **{report.completion_rate}%** across {report.total_commitments} commitments."
            )
            return {
                "reply": reply,
                "agent_name": "Reality Agent",
                "intent": "REPORT",
                "suggestions": ["What should I do right now?", "Confront my recent progress", "I accept the protocol"],
                "metadata": {"report_id": report.id, "rate": report.completion_rate}
            }

        # 4. EXCUSE CONFRONTATION INTENTS
        if any(w in lower for w in ["no time", "too busy", "busy", "swamped"]):
            self.memory.record_interaction_memory(user_id, "EXCUSE_PATTERN", f"User cited time constraint: '{message}'", ["time", "avoidance"])
            reply = (
                "\"No time.\" Let's test that claim.\n\n"
                "Everyone has the same 24 hours. Sleep is 7–8 hours. Work or study is 8 hours. That leaves 8 unallocated hours. "
                "Where did the 45 minutes for your commitment go?\n\n"
                "It is rarely lack of time. It is a matter of priority. What distraction did you prioritize over your stated goal?"
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "EXCUSE_TIME",
                "suggestions": ["I got distracted by my phone", "I will do 15 minutes right now", "What should I do right now?"]
            }

        if any(w in lower for w in ["tired", "exhausted", "sleepy", "no energy", "drained"]):
            self.memory.record_interaction_memory(user_id, "EXCUSE_PATTERN", f"User cited fatigue: '{message}'", ["fatigue", "avoidance"])
            reply = (
                "Fatigue is real, but it is also the most common rationalization for quitting.\n\n"
                "Ask yourself honestly: could you execute a focused 10-minute micro-version right now? "
                "If yes, tiredness didn't take away your ability—it just took away your mood.\n\n"
                "Start for 10 minutes right now. No debate."
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "EXCUSE_TIRED",
                "suggestions": ["Starting 10 minutes right now", "What should I do right now?", "Tomorrow at 7 AM sharp"]
            }

        if any(w in lower for w in ["tomorrow", "later", "tonight", "will do it", "i'll do it"]):
            reply = (
                "\"Tomorrow\" is the graveyard of consistency.\n\n"
                "You said tomorrow before, and that is how entire weeks evaporate. "
                "State the exact hour tomorrow you are locking this down, or execute the first 10 minutes immediately."
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "EXCUSE_TOMORROW",
                "suggestions": ["Tomorrow at 7:00 AM sharp", "Executing 10 minutes now", "What should I do right now?"]
            }

        if any(w in lower for w in ["not in the mood", "no motivation", "unmotivated", "don't feel like", "lazy"]):
            reply = (
                "Motivation is an amateur's game. Discipline is professional.\n\n"
                "You did not make these commitments based on how you would feel. You made them based on where you want to be. "
                "Open the task and work for 5 minutes. You don't have to like it—you just have to deliver."
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "EXCUSE_MOOD",
                "suggestions": ["Starting 5 minutes now", "What should I do right now?", "Review my progress"]
            }

        if any(w in lower for w in ["missed", "skipped", "didn't do", "failed to", "couldn't finish"]):
            reply = (
                "Missed commitment acknowledged. No sugarcoating: you dropped the standard.\n\n"
                "State plain facts:\n"
                "1. Exactly what prevented completion?\n"
                "2. When will you make up the deficit?\n"
                "Give me a specific timestamp, not vague intent."
            )
            return {
                "reply": reply,
                "agent_name": "Confront Agent",
                "intent": "MISSED",
                "suggestions": ["I will recover it tonight at 9 PM", "Reschedule to tomorrow morning", "What should I do right now?"]
            }

        # 5. GOAL SPECIFIC ONBOARDING INTENTS
        if any(w in lower for w in ["dsa", "leetcode", "algorithm", "coding interview"]):
            reply = (
                "DSA mastery is pure quantitative execution. No talent, just volume and reflection.\n\n"
                "Here is your baseline protocol:\n"
                "• 2 Problems Daily (1 core topic, 1 weak spot)\n"
                "• 30 Minutes Reviewing mistakes and patterns\n"
                "• 1 Timed Mock Interview weekly\n\n"
                "What is your target deadline date, and which daily time slot are you locking in?"
            )
            return {
                "reply": reply,
                "agent_name": "Onboarding Agent",
                "intent": "GOAL_DSA",
                "suggestions": ["Mornings at 7:00 AM", "By December 30th", "Lock into my board"]
            }

        if any(w in lower for w in ["gym", "workout", "fitness", "exercise", "weight loss"]):
            reply = (
                "Physical discipline drives mental discipline. The workout begins at the decision point, not the gym.\n\n"
                "Proposed Protocol:\n"
                "• 4 Sessions / week (non-negotiable)\n"
                "• Gear packed the night prior\n"
                "• 45 Minutes of focused intensity\n\n"
                "Which four days are you locking down? Monday, Tuesday, Thursday, Saturday?"
            )
            return {
                "reply": reply,
                "agent_name": "Onboarding Agent",
                "intent": "GOAL_GYM",
                "suggestions": ["Mon, Tue, Thu, Sat at 6 PM", "Mornings before work", "Lock into my board"]
            }

        # 6. GREETINGS & HELP
        if any(w in lower for w in ["hello", "hi", "hey", "sup"]):
            reply = (
                "Brutality AI online. Skip the small talk.\n\n"
                "What is the single most important commitment you need to deliver today?"
            )
            return {
                "reply": reply,
                "agent_name": "Onboarding Agent",
                "intent": "GREETING",
                "suggestions": ["What should I do right now?", "Confront my recent progress", "I want to master DSA"]
            }

        if any(w in lower for w in ["help", "how do you work", "what can you do"]):
            reply = (
                "BRUTALITY AI enforces four core operational phases:\n\n"
                "1. **Onboarding**: Converts goals into daily scheduled deliverables with strict completion criteria.\n"
                "2. **Check-ins**: Verifies real-world delivery against what you promised.\n"
                "3. **Confrontation**: Eliminates vague excuses and flags avoidance habits.\n"
                "4. **Reality Reports**: Synthesizes unvarnished weekly progress audits from database metrics.\n\n"
                "Start by checking your commitments or asking what to do right now."
            )
            return {
                "reply": reply,
                "agent_name": "Onboarding Agent",
                "intent": "HELP",
                "suggestions": ["What should I do right now?", "Confront my recent progress", "Generate my Reality Report"]
            }

        # 7. DEFAULT / COACHING FALLBACK
        mem_context = self.memory.get_user_context(user_id=user_id, query_hint=message)
        system_prompt = (
            "You are BRUTALITY AI. "
            "You are direct, disciplined, honest, constructive, and uncompromising. "
            "Help the user execute their goals. Call out avoidance and demand clarity without insulting them.\n"
            f"User memory history:\n{mem_context}"
        )
        llm_reply = self.ai.generate_text(system_prompt, message)

        return {
            "reply": llm_reply,
            "agent_name": "Confront Agent",
            "intent": "COACHING",
            "suggestions": [
                "What should I do right now?",
                "Confront my recent progress",
                "Generate my Reality Report"
            ],
            "metadata": {"has_memory_context": bool(mem_context)}
        }

