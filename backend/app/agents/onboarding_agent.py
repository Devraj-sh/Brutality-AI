from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class OnboardingAgent(BaseAgent):
    """
    AGENT 1 — ONBOARDING AGENT
    Converts user ambition into realistic, measurable, and scheduled commitments.
    Ensures tasks have explicit completion criteria and reasonable daily workloads.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="OnboardingAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Onboarding Agent. "
            "Your mission is to convert high-level user goals into concrete, measurable commitments. "
            "Rules:\n"
            "1. No generic fluff or vague habits.\n"
            "2. Break down the goal into clear sequential milestones.\n"
            "3. Generate measurable daily commitments with estimated duration and explicit completion criteria.\n"
            "4. Never generate an overwhelming or contradictory schedule.\n"
            "5. Return pure valid JSON with 'strategy_overview', 'weekly_breakdown', and 'commitments'."
        )

    def generate_plan(
        self,
        goal_title: str,
        motivation: str = "",
        current_level: str = "Intermediate",
        available_hours: float = 10.0,
        timeframe_days: int = 30,
        constraints: str = ""
    ) -> Dict[str, Any]:
        user_prompt = (
            f"Goal: {goal_title}\n"
            f"Motivation: {motivation}\n"
            f"Current Level: {current_level}\n"
            f"Available Time: {available_hours} hours/week\n"
            f"Timeframe: {timeframe_days} days\n"
            f"Constraints: {constraints}\n\n"
            "Create a structured execution plan. Return JSON in this format:\n"
            "{\n"
            '  "strategy_overview": "string",\n'
            '  "weekly_breakdown": ["Week 1: ...", "Week 2: ..."],\n'
            '  "commitments": [\n'
            '    {\n'
            '      "title": "string",\n'
            '      "description": "string",\n'
            '      "day_offset": 0,\n'
            '      "priority": "HIGH",\n'
            '      "estimated_duration": 45,\n'
            '      "completion_criteria": "string"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        response = self.ai.generate_json(self.get_system_prompt(), user_prompt)
        
        # Validate and normalize commitments
        commitments = response.get("commitments", [])
        if not commitments:
            # Fallback guarantee
            commitments = [
                {
                    "title": f"Initial Deep Dive: {goal_title}",
                    "description": "Establish the foundational groundwork and first key deliverables.",
                    "day_offset": 0,
                    "priority": "HIGH",
                    "estimated_duration": 45,
                    "completion_criteria": "45 minutes uninterrupted execution completed."
                },
                {
                    "title": f"Execution & Skill Application: {goal_title}",
                    "description": "Apply practical problem solving and deliver core project output.",
                    "day_offset": 1,
                    "priority": "HIGH",
                    "estimated_duration": 60,
                    "completion_criteria": "Core output completed and reviewed."
                }
            ]
            response["commitments"] = commitments

        # Calculate exact dates based on day_offset
        today = datetime.now(timezone.utc).date()
        for c in commitments:
            offset = int(c.get("day_offset", 0))
            task_date = today + timedelta(days=offset)
            c["scheduled_date"] = task_date.strftime("%Y-%m-%d")

        return response
