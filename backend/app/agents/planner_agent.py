from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class PlannerAgent(BaseAgent):
    """
    AGENT 4 — PLANNER AGENT
    Dynamically recalculates and adapts the execution schedule based on real performance.
    Preserves completed achievements and prevents unrealistic pile-ups.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="PlannerAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Planner Agent. "
            "Your role is to adapt future commitments based on real execution data.\n"
            "Rules:\n"
            "1. NEVER delete or overwrite completed work.\n"
            "2. Reschedule missed or blocked commitments forward without creating an impossible pile-up.\n"
            "3. Maintain realistic daily capacity (do not force 12 hours of work into tomorrow).\n"
            "4. Provide a clear, rational explanation for any schedule change.\n"
            "5. Return pure JSON with 'explanation' and 'adjustments'."
        )

    def adapt_plan(
        self,
        missed_tasks: List[Dict[str, Any]],
        upcoming_tasks: List[Dict[str, Any]],
        goal_target_date: str = ""
    ) -> Dict[str, Any]:
        if not missed_tasks:
            return {
                "explanation": "All commitments on schedule. No plan adjustments required.",
                "adjustments": []
            }

        prompt = (
            f"Missed Tasks Needing Rescheduling: {missed_tasks}\n"
            f"Upcoming Scheduled Tasks: {upcoming_tasks}\n"
            f"Target Goal Deadline: {goal_target_date}\n\n"
            "Adjust the future plan to accommodate the missed deliverables. Return JSON:\n"
            "{\n"
            '  "explanation": "Reasoning for the adjustment",\n'
            '  "adjustments": [\n'
            '    {\n'
            '      "task_id": "string",\n'
            '      "new_scheduled_date": "YYYY-MM-DD",\n'
            '      "priority": "HIGH",\n'
            '      "reason": "Why this date was chosen"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        response = self.ai.generate_json(self.get_system_prompt(), prompt)
        
        # Fallback deterministic adjustment if AI provided empty adjustments
        if not response.get("adjustments"):
            tomorrow = (datetime.now(timezone.utc).date() + timedelta(days=1)).strftime("%Y-%m-%d")
            adjustments = []
            for t in missed_tasks:
                adjustments.append({
                    "task_id": t.get("id", "task_id"),
                    "new_scheduled_date": tomorrow,
                    "priority": "HIGH",
                    "reason": "Rescheduled directly to tomorrow to prevent backlog accumulation."
                })
            response["adjustments"] = adjustments
            response["explanation"] = response.get("explanation") or "Rescheduled incomplete commitments to the next available execution window."

        return response
