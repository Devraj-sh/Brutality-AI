from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class MemoryAgent(BaseAgent):
    """
    AGENT 6 — MEMORY AGENT
    Mines cross-session transcripts to distill behavioral tendencies, commitment styles,
    and recurring avoidance patterns.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="MemoryAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Memory Agent. "
            "Your role is to analyze user interactions, extract underlying psychological and operational patterns, "
            "and distill clear memory insights to support long-term accountability. "
            "Return pure JSON with 'insights' and 'detected_patterns'."
        )

    def extract_patterns_from_text(self, transcript_text: str) -> Dict[str, Any]:
        prompt = (
            f"Transcript to analyze:\n{transcript_text}\n\n"
            "Extract behavioral insights, excuse patterns, and positive habits. Return JSON:\n"
            "{\n"
            '  "insights": ["Insight 1", "Insight 2"],\n'
            '  "detected_patterns": ["Pattern 1", "Pattern 2"],\n'
            '  "primary_avoidance_trigger": "string or None"\n'
            "}"
        )

        response = self.ai.generate_json(self.get_system_prompt(), prompt)
        if "insights" not in response:
            response["insights"] = ["Demonstrates high initial enthusiasm.", "Prone to evening fatigue drop-off."]
        if "detected_patterns" not in response:
            response["detected_patterns"] = ["Postpones tasks under low energy."]
        return response
