from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class ConfrontAgent(BaseAgent):
    """
    AGENT 3 — CONFRONT AGENT
    Core accountability intelligence: evaluates promised commitments vs actual delivery.
    Detects avoidance patterns, vague rationalizations, and classifies execution status.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="ConfrontAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Confront Agent. "
            "Your philosophy: 'An AI that remembers what you promised, tracks what you delivered, and confronts the gap.'\n"
            "Responsibilities:\n"
            "1. Evaluate the difference between what was promised and what was actually delivered.\n"
            "2. Detect vague explanations ('busy', 'tired', 'stuff came up', 'tomorrow').\n"
            "3. Identify avoidance patterns.\n"
            "4. Categorize outcome cleanly: COMPLETED, PARTIALLY_COMPLETED, MISSED, or BLOCKED.\n"
            "5. Be direct, intelligent, honest, constructive, and disciplined. NEVER insult, humiliate, or harass.\n"
            "6. Return pure JSON with status, evaluation_text, is_vague, avoidance_detected, evidence_requested, confidence_level, and recommended_action."
        )

    def evaluate_task_update(
        self,
        task_title: str,
        completion_criteria: str,
        reported_status: str,
        user_notes: str = "",
        user_memory_context: str = ""
    ) -> Dict[str, Any]:
        user_prompt = (
            f"Commitment: {task_title}\n"
            f"Completion Criteria: {completion_criteria}\n"
            f"User Reported Status: {reported_status}\n"
            f"User Explanation/Notes: {user_notes}\n"
            f"Known User Memory Patterns:\n{user_memory_context}\n\n"
            "Evaluate this check-in update objectively. Return JSON:\n"
            "{\n"
            '  "status": "COMPLETED | PARTIALLY_COMPLETED | MISSED | BLOCKED",\n'
            '  "is_vague": true/false,\n'
            '  "avoidance_detected": true/false,\n'
            '  "evidence_requested": true/false,\n'
            '  "confidence_level": 0.95,\n'
            '  "evaluation_text": "Direct, honest, non-insulting feedback confronting the gap",\n'
            '  "recommended_action": "Clear next action"\n'
            "}"
        )

        response = self.ai.generate_json(self.get_system_prompt(), user_prompt)
        
        # Fallback sanity checks
        if "status" not in response:
            response["status"] = reported_status if reported_status in ["COMPLETED", "PARTIALLY_COMPLETED", "MISSED", "BLOCKED"] else "MISSED"
        if "evaluation_text" not in response:
            response["evaluation_text"] = "Status recorded. Maintain strict standards for tomorrow's commitments."
        if "recommended_action" not in response:
            response["recommended_action"] = "Lock in tomorrow's non-negotiable target."
            
        return response
