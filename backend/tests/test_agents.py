import pytest
from app.agents.onboarding_agent import OnboardingAgent
from app.agents.checkin_agent import CheckinAgent
from app.agents.confront_agent import ConfrontAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.reality_agent import RealityAgent
from app.agents.memory_agent import MemoryAgent
from app.services.ai_service import MockAIService

@pytest.fixture
def mock_ai():
    return MockAIService()

def test_onboarding_agent_generates_commitments(mock_ai):
    agent = OnboardingAgent(mock_ai)
    plan = agent.generate_plan(
        goal_title="Master System Design",
        motivation="Land Principal Engineer offer",
        current_level="Advanced",
        available_hours=15.0,
        timeframe_days=30
    )

    assert "strategy_overview" in plan
    assert "commitments" in plan
    assert len(plan["commitments"]) >= 2
    for c in plan["commitments"]:
        assert "title" in c
        assert "scheduled_date" in c
        assert "completion_criteria" in c
        assert c["priority"] in ["HIGH", "MEDIUM", "LOW"]

def test_checkin_agent_formats_commitments(mock_ai):
    agent = CheckinAgent(mock_ai)
    sample_tasks = [
        {"id": "t1", "title": "Solve 2 LeetCode Hard", "completion_criteria": "Accepted solution", "estimated_duration": 60},
        {"id": "t2", "title": "Read Raft Consensus Paper", "completion_criteria": "Summarize leader election", "estimated_duration": 45}
    ]
    result = agent.generate_checkin_prompt(sample_tasks, user_name="Alex")

    assert "Alex" in result["message"]
    assert len(result["questions"]) == 2
    assert "LeetCode" in result["questions"][0]

def test_confront_agent_detects_excuses(mock_ai):
    agent = ConfrontAgent(mock_ai)
    result = agent.evaluate_task_update(
        task_title="Solve 2 LeetCode Hard",
        completion_criteria="Accepted solution",
        reported_status="MISSED",
        user_notes="I was too busy and tired today so I will do it tomorrow.",
        user_memory_context="Previous fatigue excuses logged."
    )

    assert result["status"] in ["MISSED", "PARTIALLY_COMPLETED"]
    assert result["is_vague"] is True
    assert result["avoidance_detected"] is True
    assert "evaluation_text" in result
    assert "recommended_action" in result

def test_planner_agent_adapts_without_deleting_history(mock_ai):
    agent = PlannerAgent(mock_ai)
    missed = [{"id": "t1", "title": "Missed Task"}]
    upcoming = [{"id": "t2", "title": "Upcoming Task", "scheduled_date": "2026-11-20"}]

    plan = agent.adapt_plan(missed_tasks=missed, upcoming_tasks=upcoming)
    assert "explanation" in plan
    assert "adjustments" in plan
    assert len(plan["adjustments"]) > 0
    assert plan["adjustments"][0]["task_id"] in ["t1", "target"]

def test_reality_agent_synthesizes_deterministic_report(mock_ai):
    agent = RealityAgent(mock_ai)
    report = agent.generate_reality_report(
        total_tasks=10,
        completed_tasks=7,
        missed_tasks=3,
        completion_rate=70.0,
        recent_excuses=["I was too tired in the evening"]
    )

    assert "brutal_truth" in report
    assert "excuse_analysis" in report
    assert "strengths" in report
    assert "action_plan" in report

def test_memory_agent_extracts_patterns(mock_ai):
    agent = MemoryAgent(mock_ai)
    res = agent.extract_patterns_from_text("User repeatedly delays morning workouts due to late screen time.")
    assert "insights" in res
    assert "detected_patterns" in res
