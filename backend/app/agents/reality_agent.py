from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.ai_service import BaseAIService

class RealityAgent(BaseAgent):
    """
    AGENT 5 — REALITY AGENT
    Replaces punishment schemes with clear, unvarnished accountability and deterministic data.
    Synthesizes weekly Reality Reports based strictly on verified execution metrics.
    """

    def __init__(self, ai_service: BaseAIService = None):
        super().__init__(name="RealityAgent", ai_service=ai_service)

    def get_system_prompt(self) -> str:
        return (
            "You are the BRUTALITY AI Reality Agent. "
            "Your job is to provide unvarnished, data-backed truth regarding user execution. "
            "Never use insults or harassment. Focus purely on the contrast between commitments and delivery. "
            "Highlight both legitimate strengths and recurring avoidance habits. "
            "Return pure JSON with 'brutal_truth', 'excuse_analysis', 'strengths', and 'action_plan'."
        )

    def generate_reality_report(
        self,
        total_tasks: int,
        completed_tasks: int,
        missed_tasks: int,
        completion_rate: float,
        recent_excuses: List[str] = None,
        goals_summary: str = ""
    ) -> Dict[str, Any]:
        prompt = (
            f"Execution Statistics:\n"
            f"- Total Commitments: {total_tasks}\n"
            f"- Completed: {completed_tasks}\n"
            f"- Missed/Incomplete: {missed_tasks}\n"
            f"- Completion Rate: {completion_rate}%\n"
            f"- User Goals: {goals_summary}\n"
            f"- Recorded Excuses: {recent_excuses or ['None logged']}\n\n"
            "Synthesize an authoritative Brutality Reality Report. Return JSON:\n"
            "{\n"
            '  "brutal_truth": "Direct assessment of performance vs potential",\n'
            '  "excuse_analysis": "Diagnostic of why commitments were dropped",\n'
            '  "strengths": "Verified capabilities and consistent wins",\n'
            '  "action_plan": "Specific operational protocols for the upcoming cycle"\n'
            "}"
        )

        response = self.ai.generate_json(self.get_system_prompt(), prompt)
        
        # Ensure non-empty keys
        if "brutal_truth" not in response or not response["brutal_truth"]:
            response["brutal_truth"] = (
                f"You achieved a {completion_rate}% delivery rate across {total_tasks} commitments. "
                "Execution is respectable when friction is low, but discipline breaks down when resistance appears."
            )
        if "excuse_analysis" not in response or not response["excuse_analysis"]:
            response["excuse_analysis"] = "Avoidance primarily occurs under fatigue or vague scheduling."
        if "strengths" not in response or not response["strengths"]:
            response["strengths"] = "Demonstrated capacity to finish high-priority tasks when clearly defined."
        if "action_plan" not in response or not response["action_plan"]:
            response["action_plan"] = "Lock in execution windows 24 hours prior. Zero same-day rescheduling."

        return response
