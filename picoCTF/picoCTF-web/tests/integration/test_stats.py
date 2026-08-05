"""Tests for the /api/v1/stats endpoints."""
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
    cache,
    RATE_LIMIT_BYPASS_KEY,
    update_all_scoreboards,
)
import api


def test_registration_stats(mongo_proc, redis_proc, client):
    """Test the /stats/registration endpoint."""
    clear_db()
    register_test_accounts()

    # Get the initial registration count
    res = client.get("/api/v1/stats/registration")
    assert res.status_code == 200
    expected_response = {
        "groups": 0,
        "teamed_users": 0,
        "teams": 0,
        "users": 5,
        "teachers": 1,
    }
    assert res.json == expected_response

    # Try adding a new user
    res = client.post(
        "/api/v1/users",
        json={
            "email": "user3@sample.com",
            "firstname": "Third",
            "lastname": "Testuser",
            "password": "testuser3",
            "username": "testuser3",
            "affiliation": "Testing",
            "usertype": "other",
            "country": "US",
            "demo": {"age": "18+"},
        },
    )
    assert res.status_code == 201
    cache(api.stats.get_registration_count)
    res = client.get("/api/v1/stats/registration")
    assert res.status_code == 200
    expected_response["users"] += 1
    assert res.json == expected_response

    # Have a user create a team
    client.post(
        "api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
    )
    res = client.post(
        "/api/v1/teams", json={"team_name": "newteam", "team_password": "newteam"}
    )
    assert res.status_code == 201

    cache(api.stats.get_registration_count)
    res = client.get("/api/v1/stats/registration")
    assert res.status_code == 200
    expected_response["teams"] += 1
    expected_response["teamed_users"] += 1
    assert res.json == expected_response

    # Have another user join that team
    api.config.get_settings()
    db = get_conn()
    db.settings.find_one_and_update({}, {"$set": {"max_team_size": 2}})
    client.get("/api/v1/user/logout")
    client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_2_DEMOGRAPHICS["username"],
            "password": STUDENT_2_DEMOGRAPHICS["password"],
        },
    )
    res = client.post(
        "/api/v1/team/join", json={"team_name": "newteam", "team_password": "newteam"}
    )
    assert res.status_code == 200

    cache(api.stats.get_registration_count)
    res = client.get("/api/v1/stats/registration")
    assert res.status_code == 200
    expected_response["teamed_users"] += 1
    assert res.json == expected_response

    # Create a group
    client.get("/api/v1/user/logout")
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": TEACHER_DEMOGRAPHICS["username"],
            "password": TEACHER_DEMOGRAPHICS["password"],
        },
    )
    csrf_t = get_csrf_token(res)
    res = client.post(
        "/api/v1/groups", json={"name": "newgroup"}, headers=[("X-CSRF-Token", csrf_t)]
    )
    print(res.json)
    assert res.status_code == 201

    cache(api.stats.get_registration_count)
    res = client.get("/api/v1/stats/registration")
    assert res.status_code == 200
    expected_response["groups"] += 1
    assert res.json == expected_response
