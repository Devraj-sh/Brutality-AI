import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("brutality_ai.ai_service")

class BaseAIService:
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class MockAIService(BaseAIService):
    """
    Deterministic AI mock engine that generates high-fidelity structured responses
    matching the exact Brutality AI voice and schema expectations.
    """

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        user_lower = user_prompt.lower()
        sys_lower = system_prompt.lower()

        # Onboarding Plan Generation
        if "onboarding" in sys_lower or "execution plan" in sys_lower:
            return {
                "strategy_overview": "A disciplined, step-by-step commitment framework designed to turn ambition into non-negotiable daily execution.",
                "weekly_breakdown": [
                    "Week 1: Foundations and core habit lockdown.",
                    "Week 2: Increasing intensity and volume.",
                    "Week 3: Stress-testing under fatigue.",
                    "Week 4: Final delivery and retrospective review."
                ],
                "commitments": [
                    {
                        "title": "Establish Baseline Execution",
                        "description": "Complete 45 minutes of focused core work without distraction.",
                        "day_offset": 0,
                        "priority": "HIGH",
                        "estimated_duration": 45,
                        "completion_criteria": "45 minutes uninterrupted focus logged."
                    },
                    {
                        "title": "Deep Technical Drills",
                        "description": "Execute targeted problem solving and concept mastery.",
                        "day_offset": 1,
                        "priority": "HIGH",
                        "estimated_duration": 60,
                        "completion_criteria": "2 complex problems solved and documented."
                    },
                    {
                        "title": "Review & Flaw Elimination",
                        "description": "Examine errors, analyze weaknesses, and iterate.",
                        "day_offset": 2,
                        "priority": "MEDIUM",
                        "estimated_duration": 30,
                        "completion_criteria": "Weakness audit completed with notes."
                    }
                ]
            }

        # Confront Agent Evaluation
        if "confront" in sys_lower:
            is_vague = any(w in user_lower for w in ["busy", "tired", "later", "tomorrow", "didnt feel like", "stuff came up"])
            
            status = "COMPLETED"
            if "user reported status: missed" in user_lower:
                status = "MISSED"
            elif "user reported status: partially_completed" in user_lower:
                status = "PARTIALLY_COMPLETED"
            elif "user reported status: blocked" in user_lower:
                status = "BLOCKED"
            elif is_vague:
                status = "MISSED"



            return {
                "status": status,
                "is_vague": is_vague,
                "avoidance_detected": is_vague,
                "evidence_requested": False,
                "confidence_level": 0.95,
                "evaluation_text": (
                    "Vagueness detected. You cited low energy or competing priorities, but that was not part of your commitment. Be honest about why the priority dropped."
                    if is_vague else
                    "Commitment delivered cleanly. No excuses found. Keep stacking uninterrupted execution."
                ),
                "recommended_action": "Reschedule the deficit immediately and lock in tomorrow's non-negotiable target."
            }

        # Planner Agent Adaptation
        if "planner" in sys_lower:
            return {
                "explanation": "Adapted upcoming commitments to absorb missed targets without lowering overall standards or overloading the schedule.",
                "adjustments": [
                    {
                        "task_id": "target",
                        "new_scheduled_date": "next_day",
                        "priority": "HIGH",
                        "reason": "Rescheduled from missed commitment without extending the final deadline."
                    }
                ]
            }

        # Reality Agent Report
        if "reality" in sys_lower:
            return {
                "brutal_truth": "You executed on scheduled tasks when convenient, but your consistency faltered when external friction appeared.",
                "excuse_analysis": "Primary excuse pattern: claiming fatigue and postponing to 'tomorrow'. Tomorrow is not a strategy.",
                "strengths": "High velocity when momentum is active; demonstrated technical competence on early commitments.",
                "action_plan": "1. Set non-negotiable morning execution window. 2. Eliminate evening excuses. 3. Zero rollover tolerance."
            }

        # Fallback default JSON
        return {
            "status": "PROCESSED",
            "message": "AI processed input successfully.",
            "data": {}
        }

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        user_lower = user_prompt.lower()
        if "hello" in user_lower or "hi" in user_lower:
            return "State your target clearly. Brutality AI is listening. What are we building or conquering today?"
        if "tired" in user_lower or "can't" in user_lower:
            return "Fatigue is information, not an excuse to quit. Break the task down, execute the first 10 minutes, and evaluate after."
        return "Understood. The commitment is noted. Your execution will speak louder than your explanation."


class OpenAIService(BaseAIService):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt + "\nYou must return pure valid JSON."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI call failed ({e}). Falling back to MockAIService.")
            return MockAIService().generate_json(system_prompt, user_prompt)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"OpenAI call failed ({e}). Falling back to MockAIService.")
            return MockAIService().generate_text(system_prompt, user_prompt)


def get_ai_service() -> BaseAIService:
    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAIService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI service ({e}). Using mock.")
    return MockAIService()
