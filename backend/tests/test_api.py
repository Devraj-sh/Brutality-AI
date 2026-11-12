import pytest

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "brutality ai" in res.json()["service"].lower()


def test_auth_registration_and_login(client):
    # 1. Register
    reg_payload = {
        "email": "cadet@brutality.ai",
        "password": "unbreakable_will",
        "full_name": "Cadet One"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "cadet@brutality.ai"

    # 2. Login
    login_payload = {
        "email": "cadet@brutality.ai",
        "password": "unbreakable_will"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

    # 3. /me with token
    token = res_login.json()["access_token"]
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["full_name"] == "Cadet One"

def test_onboarding_api(client, auth_headers):
    payload = {
        "primary_goal": "Run a Half Marathon in 60 Days",
        "motivation": "Build raw discipline and mental fortitude",
        "current_level": "Beginner",
        "available_hours_per_week": 6.0,
        "timeframe_days": 60
    }
    res = client.post("/api/onboarding/start", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert "goal" in data
    assert data["goal"]["title"] == payload["primary_goal"]
    assert len(data["commitments_created"]) >= 2

def test_goals_crud_api(client, auth_headers):
    # Create goal
    create_payload = {
        "title": "Publish Technical Research Paper",
        "category": "Career",
        "motivation": "Establish industry authority",
        "target_date": "2026-12-31"
    }
    res = client.post("/api/goals", json=create_payload, headers=auth_headers)
    assert res.status_code == 201
    goal = res.json()
    goal_id = goal["id"]
    assert goal["title"] == create_payload["title"]

    # Read all goals
    res_list = client.get("/api/goals", headers=auth_headers)
    assert res_list.status_code == 200
    assert any(g["id"] == goal_id for g in res_list.json())

    # Update goal
    res_update = client.put(f"/api/goals/{goal_id}", json={"progress": 25}, headers=auth_headers)
    assert res_update.status_code == 200
    assert res_update.json()["progress"] == 25

    # Delete goal
    res_del = client.delete(f"/api/goals/{goal_id}", headers=auth_headers)
    assert res_del.status_code == 204

def test_tasks_crud_api(client, auth_headers):
    # Create task
    task_payload = {
        "title": "Complete 50 Pushups Every Morning",
        "scheduled_date": "2026-11-15",
        "priority": "HIGH",
        "estimated_duration": 15,
        "completion_criteria": "Strict form without stopping"
    }
    res = client.post("/api/tasks", json=task_payload, headers=auth_headers)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]
    assert task["title"] == task_payload["title"]

    # Filter tasks by scheduled_date
    res_filter = client.get(f"/api/tasks?scheduled_date=2026-11-15", headers=auth_headers)
    assert res_filter.status_code == 200
    assert len(res_filter.json()) >= 1

    # Update task
    res_update = client.put(f"/api/tasks/{task_id}", json={"status": "COMPLETED"}, headers=auth_headers)
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "COMPLETED"

def test_dashboard_api(client, auth_headers):
    res_stats = client.get("/api/dashboard/stats", headers=auth_headers)
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "completion_rate" in stats
    assert "consistency_score" in stats

    res_sum = client.get("/api/dashboard/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert "accountability_status" in summary
    assert "today_commitments" in summary

def test_chat_message_api(client, auth_headers):
    chat_payload = {"message": "I feel like slacking off today."}
    res = client.post("/api/chat/message", json=chat_payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 5
