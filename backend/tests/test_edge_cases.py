import pytest

def test_duplicate_registration_prevented(client):
    payload = {
        "email": "unique_warrior@brutality.ai",
        "password": "iron_discipline_1",
        "full_name": "Unique Warrior"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration should fail with 400
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_invalid_login_rejected(client):
    res = client.post("/api/auth/login", json={"email": "nonexistent@brutality.ai", "password": "wrong"})
    assert res.status_code == 401

def test_multi_user_data_isolation(client, db_session):
    # Register User A
    user_a_res = client.post("/api/auth/register", json={
        "email": "usera@brutality.ai",
        "password": "passwordA123",
        "full_name": "User Alpha"
    }).json()
    token_a = user_a_res["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register User B
    user_b_res = client.post("/api/auth/register", json={
        "email": "userb@brutality.ai",
        "password": "passwordB123",
        "full_name": "User Beta"
    }).json()
    token_b = user_b_res["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a private goal
    goal_a = client.post(
        "/api/goals",
        json={"title": "User A Classified Objective", "category": "Intel"},
        headers=headers_a
    ).json()

    # User B attempts to access User A's goal -> Must return 404
    forbidden_res = client.get(f"/api/goals/{goal_a['id']}", headers=headers_b)
    assert forbidden_res.status_code == 404

    # User B queries their own goals -> should be empty
    goals_b = client.get("/api/goals", headers=headers_b).json()
    assert len(goals_b) == 0

def test_nonexistent_entity_404(client, auth_headers):
    res = client.get("/api/tasks/fake-nonexistent-id", headers=auth_headers)
    assert res.status_code == 404

def test_malformed_token_rejected(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer malformed.token.value"})
    assert res.status_code == 401
