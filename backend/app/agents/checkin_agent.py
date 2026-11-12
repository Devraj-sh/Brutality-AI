from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class CheckinAgent(BaseAgent):
    """
    AGENT 2 — CHECK-IN AGENT
    Conducts personalized daily accountability check-ins based on scheduled commitments.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="CheckinAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Check-in Agent. "
            "Your role is to conduct direct, sharp, and personalized daily accountability check-ins. "
            "You ask the user specifically about the commitments they promised to deliver today. "
            "Be direct, disciplined, and focused on actual outcomes, not feelings or vague good intentions."
        )

    def generate_checkin_prompt(self, tasks: List[Dict[str, Any]], user_name: str = "Warrior") -> Dict[str, Any]:
        if not tasks:
            return {
                "message": f"Zero commitments were scheduled for today, {user_name}. Was this intentional recovery, or did you fail to plan?",
                "tasks": [],
                "questions": ["What high-value progress did you make today toward your overarching goals?"]
            }

        task_summaries = []
        questions = []
        for idx, t in enumerate(tasks, 1):
            title = t.get("title", f"Task #{idx}")
            criteria = t.get("completion_criteria", "Complete the required standard")
            duration = t.get("estimated_duration", 45)
            task_summaries.append(f"{idx}. {title} (Est: {duration}m | Target: {criteria})")
            questions.append(f"Did you complete '{title}' according to your stated criteria: '{criteria}'?")

        message = (
            f"Accountability Check-in for {user_name}.\n"
            f"Today you were committed to {len(tasks)} delivery item{'s' if len(tasks) > 1 else ''}:\n"
            + "\n".join(task_summaries)
            + "\n\nProvide an honest update for each item. Did you execute or make excuses?"
        )

        return {
            "message": message,
            "tasks": tasks,
            "questions": questions
        }
