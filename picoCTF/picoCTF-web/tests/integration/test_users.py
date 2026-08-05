"""Tests for the /api/v1/users endpoints."""
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
    get_conn,
    RATE_LIMIT_BYPASS_KEY,
)
import api


def test_get_users(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the GET /users endpoint."""
    clear_db()
    register_test_accounts()
    client.post(
        "/api/v1/user/login",
        json={
            "username": ADMIN_DEMOGRAPHICS["username"],
            "password": ADMIN_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )

    res = client.get("/api/v1/users")
    assert res.status_code == 200
    assert len(res.json) == 5
    for username in [
        ADMIN_DEMOGRAPHICS["username"],
        STUDENT_DEMOGRAPHICS["username"],
        STUDENT_2_DEMOGRAPHICS["username"],
        OTHER_USER_DEMOGRAPHICS["username"],
        TEACHER_DEMOGRAPHICS["username"],
    ]:
        assert username in str(res.json)


def test_add_user(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the POST /users endpoint."""
    clear_db()

    # Attempt to specify an invalid age (this field is verified in the route)
    res = client.post(
        "/api/v1/users",
        json={
            "email": "admin@sample.com",
            "firstname": "Adminuser",
            "lastname": "Test",
            "password": "adminuser",
            "username": "adminuser",
            "affiliation": "Testing",
            "usertype": "other",
            "country": "US",
            "demo": {"age": "invalid"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == "'age' must be specified in the 'demo' object. Valid values "
        + "are: ['13-17', '18+']"
    )

    # Force-enable the parent verification email setting and submit without
    api.config.get_settings()
    db = get_conn()
    db.settings.find_one_and_update(
        {}, {"$set": {"email.parent_verification_email": True}}
    )
    res = client.post(
        "/api/v1/users",
        json={
            "email": "admin@sample.com",
            "firstname": "Adminuser",
            "lastname": "Test",
            "password": "adminuser",
            "username": "adminuser",
            "affiliation": "Testing",
            "usertype": "other",
            "country": "US",
            "demo": {"age": "13-17"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 400
    assert (
        res.json["message"]
        == "Must provide a valid parent email address under the key "
        + "'demo.parentemail'."
    )

    # Attempt to specify a non-alphanumeric username
    res = client.post(
        "/api/v1/users",
        json={
            "email": "admin@sample.com",
            "firstname": "Adminuser",
            "lastname": "Test",
            "password": "adminuser",
            "username": "invalid-username!",
            "affiliation": "Testing",
            "usertype": "other",
            "country": "US",
            "demo": {"age": "13-17", "parentemail": "parent@sample.com"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 400
    assert res.json["message"] == "Usernames must be alphanumeric."

    # Create the user and verify properties
    res = client.post(
        "/api/v1/users",
        json={
            "email": "admin@sample.com",
            "firstname": "Adminuser",
            "lastname": "Test",
            "password": "adminuser",
            "username": "adminuser",
            "affiliation": "Testing",
            "usertype": "other",
            "country": "US",
            "demo": {"age": "13-17", "parentemail": "parent@sample.com"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["success"] is True
    uid = res.json["uid"]

    admin_user = db.users.find_one({"uid": uid})
    assert admin_user["email"] == "admin@sample.com"
    assert admin_user["firstname"] == "Adminuser"
    assert admin_user["lastname"] == "Test"
    assert admin_user["username"] == "adminuser"
    assert admin_user["usertype"] == "other"
    assert admin_user["country"] == "US"
    assert admin_user["demo"] == {"age": "13-17", "parentemail": "parent@sample.com"}
    assert admin_user["disabled"] is False
    assert admin_user["verified"] is True
    assert admin_user["extdata"] == {}
    assert admin_user["completed_minigames"] == []
    assert admin_user["unlocked_walkthroughs"] == []
    assert admin_user["tokens"] == 0
    assert admin_user["teacher"] is True
    assert admin_user["admin"] is True
    for other_field in ["uid", "tid", "password_hash"]:
        assert other_field in admin_user
    assert "affiliation" not in admin_user
    assert "password" not in admin_user

    admin_team = db.teams.find_one({"tid": admin_user["tid"]})
    assert admin_team["team_name"] == "adminuser"
    assert admin_team["affiliation"] == "Testing"
    assert admin_team["size"] == 1
    for other_field in ["tid", "password", "instances"]:
        assert other_field in admin_team

    # Create a teacher user and verify its roles
    res = client.post(
        "/api/v1/users",
        json={
            "email": "teacher@sample.com",
            "firstname": "Teacheruser",
            "lastname": "Test",
            "password": "teacheruser",
            "username": "teacheruser",
            "affiliation": "Testing",
            "usertype": "teacher",
            "country": "US",
            "demo": {"age": "18+"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["success"] is True
    uid = res.json["uid"]
    teacher_user = db.users.find_one({"uid": uid})
    assert teacher_user["teacher"] is True
    assert teacher_user["admin"] is False

    # Create a standard user and verify its roles
    res = client.post(
        "/api/v1/users",
        json={
            "email": "user@sample.com",
            "firstname": "Testuser",
            "lastname": "Test",
            "password": "testuser",
            "username": "testuser",
            "affiliation": "Testing",
            "usertype": "student",
            "country": "US",
            "demo": {"age": "18+"},
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 201
    assert res.json["success"] is True
    uid = res.json["uid"]
    teacher_user = db.users.find_one({"uid": uid})
    assert teacher_user["teacher"] is False
    assert teacher_user["admin"] is False


def test_get_one_user(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the GET /users/<uid> endpoint."""
    clear_db()
    register_test_accounts()
    client.post(
        "/api/v1/user/login",
        json={
            "username": ADMIN_DEMOGRAPHICS["username"],
            "password": ADMIN_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )

    db = get_conn()
    test_account_uid = db.users.find_one(
        {"username": STUDENT_DEMOGRAPHICS["username"]}
    )["uid"]

    # Attempt to get nonexistent user
    res = client.get("/api/v1/users/invalid")
    assert res.status_code == 404
    assert res.json["message"] == "User not found"

    # Get a valid user
    res = client.get(f"/api/v1/users/{test_account_uid}")
    assert res.status_code == 200
    assert STUDENT_DEMOGRAPHICS["username"] in str(res.json)
