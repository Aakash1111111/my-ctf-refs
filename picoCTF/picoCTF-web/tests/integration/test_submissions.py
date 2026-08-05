"""Tests for the /api/v1/submissions endpoints."""
from pytest_mongo import factories
from pytest_redis import factories
from .common import (  # noqa (fixture)
    ADMIN_DEMOGRAPHICS,
    clear_db,
    client,
    decode_response,
    get_csrf_token,
    register_test_accounts,
    TEACHER_DEMOGRAPHICS,
    STUDENT_DEMOGRAPHICS,
    STUDENT_2_DEMOGRAPHICS,
    OTHER_USER_DEMOGRAPHICS,
    load_sample_problems,
    get_conn,
    ensure_within_competition,
    enable_sample_problems,
    get_problem_key,
    RATE_LIMIT_BYPASS_KEY,
)
import api


def test_submission(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Test the POST /submissions endpoint."""
    clear_db()
    register_test_accounts()
    load_sample_problems()
    enable_sample_problems()
    ensure_within_competition()
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
    )
    csrf_t = get_csrf_token(res)

    # Attempt to submit a solution for a non-unlocked problem
    res = client.post(
        "/api/v1/submissions",
        json={"pid": "invalid", "key": "flag", "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 422
    assert (
        res.json["message"]
        == "You can't submit flags to problems " + "you haven't unlocked."
    )

    # Test incorrect & not previously submitted
    res = client.get("/api/v1/problems")
    unlocked_pids = [problem["pid"] for problem in res.json]
    unlocked_pids = sorted(unlocked_pids)

    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[0], "key": "invalid", "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is False
    assert res.json["message"] == "That is incorrect!"

    # Test correct & not previously submitted
    db = get_conn()
    flags = {}
    for pid in unlocked_pids:
        flags[pid] = get_problem_key(pid, STUDENT_DEMOGRAPHICS["username"])
    correct_key = flags[unlocked_pids[0]]

    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[0], "key": correct_key, "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is True
    assert res.json["message"] == "That is correct!"

    # Test incorrect & previously solved by user
    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[0], "key": "invalid", "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is False
    assert (
        res.json["message"]
        == "Flag incorrect: please note that you " + "have already solved this problem."
    )

    # Test correct & previously solved by user
    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[0], "key": correct_key, "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is True
    assert (
        res.json["message"]
        == "Flag correct: however, you have " + "already solved this problem."
    )

    # Add another player to user's team and solve a problem with them
    api.config.get_settings()
    db.settings.find_one_and_update({}, {"$set": {"max_team_size": 2}})

    client.post(
        "/api/v1/teams", json={"team_name": "newteam", "team_password": "newteam"}
    )

    client.get("/api/v1/user/logout")
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_2_DEMOGRAPHICS["username"],
            "password": STUDENT_2_DEMOGRAPHICS["password"],
        },
    )
    csrf_t = get_csrf_token(res)
    client.post(
        "/api/v1/team/join", json={"team_name": "newteam", "team_password": "newteam"}
    )

    res = client.get("/api/v1/problems")
    unlocked_pids = [problem["pid"] for problem in res.json]
    unlocked_pids = sorted(unlocked_pids)
    flags = {}
    for pid in unlocked_pids:
        flags[pid] = get_problem_key(pid, "newteam")
    correct_key = flags[unlocked_pids[1]]

    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[1], "key": correct_key, "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is True

    # Test incorrect & previously solved by another team member
    client.get("/api/v1/user/logout")
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
    )
    csrf_t = get_csrf_token(res)

    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[1], "key": "invalid", "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is False
    assert (
        res.json["message"]
        == "Flag incorrect: please note that "
        + "someone on your team has already solved this problem."
    )

    # Test correct & previously solved by another team member
    res = client.post(
        "/api/v1/submissions",
        json={"pid": unlocked_pids[1], "key": correct_key, "method": "testing"},
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["correct"] is True
    assert (
        res.json["message"]
        == "Flag correct: however, your team has "
        + "already received points for this flag."
    )


def test_clear_all_submissions(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Test the DELETE /submissions endpoint."""
    clear_db()
    register_test_accounts()
    load_sample_problems()
    enable_sample_problems()
    ensure_within_competition()
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": ADMIN_DEMOGRAPHICS["username"],
            "password": ADMIN_DEMOGRAPHICS["password"],
        },
    )
    csrf_t = get_csrf_token(res)

    # Fill the database with some submissions
    res = client.get("/api/v1/problems")
    unlocked_pids = [problem["pid"] for problem in res.json]
    unlocked_pids = sorted(unlocked_pids)
    flags = {}
    for pid in unlocked_pids:
        flags[pid] = get_problem_key(pid, ADMIN_DEMOGRAPHICS["username"])

    for pid in unlocked_pids:
        res = client.post(
            "/api/v1/submissions",
            json={"pid": pid, "key": "invalid", "method": "testing"},
            headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
        )
        res = client.post(
            "/api/v1/submissions",
            json={"pid": pid, "key": flags[pid], "method": "testing"},
            headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
        )
    db = get_conn()
    assert db.submissions.count_documents({}) == 6

    # Attempt to clear submissions without debug mode enabled
    res = client.delete("/api/v1/submissions")
    assert res.status_code == 500
    assert res.json["message"] == "Debug mode must be enabled"

    # Clear submissions
    api.submissions.DEBUG_KEY = "test"
    res = client.delete("/api/v1/submissions")
    assert res.status_code == 200
    assert res.json["success"] is True
    assert db.submissions.count_documents({}) == 0
    api.submissions.DEBUG_KEY = None
