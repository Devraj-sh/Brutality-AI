from datetime import datetime, timezone

def test_complete_brutality_accountability_workflow(client, auth_headers):
    # STEP 1: Onboard primary goal
    onboard_res = client.post(
        "/api/onboarding/start",
        json={
            "primary_goal": "Crack FAANG Staff Software Engineer Interview",
            "motivation": "Break financial barrier and operate at top tier",
            "current_level": "Senior",
            "available_hours_per_week": 14.0,
            "timeframe_days": 45
        },
        headers=auth_headers
    )
    assert onboard_res.status_code == 201
    plan_data = onboard_res.json()
    created_tasks = plan_data["commitments_created"]
    assert len(created_tasks) >= 2

    first_task = created_tasks[0]
    second_task = created_tasks[1]
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Ensure both tasks are set to today for check-in evaluation
    client.put(f"/api/tasks/{first_task['id']}", json={"scheduled_date": today_str}, headers=auth_headers)
    client.put(f"/api/tasks/{second_task['id']}", json={"scheduled_date": today_str}, headers=auth_headers)

    # STEP 2: Query today's checkin context (Agent 2)
    checkin_prep = client.get("/api/checkins/today", headers=auth_headers)
    assert checkin_prep.status_code == 200
    prep_data = checkin_prep.json()
    assert "questions" in prep_data

    # STEP 3: Submit Check-in with mixed execution & excuse (Agent 3 Confront + Agent 4 Planner)
    submission_payload = {
        "date": today_str,
        "task_updates": [
            {
                "task_id": first_task["id"],
                "reported_status": "COMPLETED",
                "user_notes": "Solved dynamic programming problem with optimal memoization.",
                "evidence_url": "https://github.com/my-solutions/dp-1.py"
            },
            {
                "task_id": second_task["id"],
                "reported_status": "MISSED",
                "user_notes": "I was exhausted and busy with chores so I postponed it."
            }
        ],
        "overall_reflection": "Managed the hard technical work but dropped the ball on second task."
    }

    eval_res = client.post("/api/checkins/submit", json=submission_payload, headers=auth_headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()

    # Verify Confront Agent flagged the excuse
    assert eval_data["overall_status"] in ["AVOIDANCE_DETECTED", "PARTIAL"]
    assert "confrontation" in eval_data["brutal_feedback"].lower() or len(eval_data["task_evaluations"]) == 2

    eval_task_2 = [te for te in eval_data["task_evaluations"] if te["task_id"] == second_task["id"]][0]
    assert eval_task_2["avoidance_detected"] is True or eval_task_2["is_vague"] is True

    # Verify Planner Agent adjusted the schedule forward
    assert eval_data["planner_applied"] is True

    # Verify completed task 1 was preserved as COMPLETED
    t1_check = client.get(f"/api/tasks/{first_task['id']}", headers=auth_headers).json()
    assert t1_check["status"] == "COMPLETED"

    # STEP 4: Synthesize Reality Report (Agent 5)
    report_res = client.post("/api/reports/reality/generate", headers=auth_headers)
    assert report_res.status_code == 201
    report_data = report_res.json()

    assert report_data["total_commitments"] >= 2
    assert report_data["completed_commitments"] >= 1
    assert "brutal_truth" in report_data
    assert "excuse_analysis" in report_data
    assert "action_plan" in report_data
