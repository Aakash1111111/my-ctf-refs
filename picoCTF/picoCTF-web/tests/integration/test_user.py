"""Tests for the /api/v1/user endpoints."""
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
    get_conn,
    RATE_LIMIT_BYPASS_KEY,
)
import api
from re import match


def test_login(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Test the /user/login endpoint."""
    clear_db()
    register_test_accounts()

    # Attempt to login with a malformed request
    res = client.post(
        "/api/v1/user/login",
        json={"username": "invalid"},
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 400

    # Attempt to login with an invalid username
    res = client.post(
        "/api/v1/user/login",
        json={"username": "invalid", "password": "invalid"},
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 401
    assert res.json["message"] == "Incorrect username."

    # Attempt to login with an incorrect password
    res = client.post(
        "/api/v1/user/login",
        json={"username": STUDENT_DEMOGRAPHICS["username"], "password": "invalid"},
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 401
    assert res.json["message"] == "Incorrect password"

    # Force-disable account and attempt to login
    db = get_conn()
    db.users.update(
        {"username": STUDENT_DEMOGRAPHICS["username"]}, {"$set": {"disabled": True}}
    )
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 403
    assert res.json["message"] == "This account has been deleted."
    db.users.update(
        {"username": STUDENT_DEMOGRAPHICS["username"]}, {"$set": {"disabled": False}}
    )

    # Force un-verify account and attempt to login
    db = get_conn()
    db.users.update(
        {"username": STUDENT_DEMOGRAPHICS["username"]}, {"$set": {"verified": False}}
    )
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 403
    assert (
        res.json["message"]
        == "This account has not been verified yet. An additional email has been sent to student@example.com."
    )
    db.users.update(
        {"username": STUDENT_DEMOGRAPHICS["username"]}, {"$set": {"verified": True}}
    )

    # Successfully log in
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True
    assert res.json["username"] == STUDENT_DEMOGRAPHICS["username"]


def test_login_rate_limit(mongo_proc, redis_proc, client):  # noqa (fixture)
    regex = r"Too many requests, slow down! Limit: (\d*), (\d*)s duration"
    # Repeated attempts to login with an incorrect password
    res = None
    for _ in range(21):
        res = client.post(
            "/api/v1/user/login",
            json={"username": STUDENT_DEMOGRAPHICS["username"], "password": "invalid"},
        )
    assert res.status_code == 429
    assert match(regex, res.json["message"]) is not None

    # Repeated attempts to login with an incorrect password, wrong bypass
    for _ in range(21):
        res = client.post(
            "/api/v1/user/login",
            json={"username": STUDENT_DEMOGRAPHICS["username"], "password": "invalid"},
            headers=[("Limit-Bypass", "invalid")],
        )
    assert res.status_code == 429
    assert match(regex, res.json["message"]) is not None

    # Attempt to login with an incorrect password, correct bypass,
    # immediately following rate_limit state

    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True


def test_logout(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Test the /user/logout endpont."""
    clear_db()
    register_test_accounts()

    # Attempt to log out without being logged in
    res = client.get("/api/v1/user/logout")
    assert res.status_code == 401
    assert res.json["message"] == "You must be logged in"

    # Successfully log out
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    res = client.get("/api/v1/user/logout")
    assert res.status_code == 200
    assert res.json["success"] is True


def test_authorize(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Test the /user/authorize endpoint."""
    clear_db()
    register_test_accounts()

    # Test invalid role
    res = client.get("/api/v1/user/authorize/invalid")
    assert res.status_code == 401
    assert res.json["message"] == "Invalid role"

    # Test "anonymous" role
    expected_body = {"anonymous": True, "user": False, "teacher": False, "admin": False}
    res = client.get("/api/v1/user/authorize/user")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/teacher")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/admin")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/anonymous")
    assert res.status_code == 200
    assert res.json == expected_body

    # Test "user" role
    expected_body = {"anonymous": True, "user": True, "teacher": False, "admin": False}
    client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    res = client.get("/api/v1/user/authorize/user")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/teacher")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/admin")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/anonymous")
    assert res.status_code == 200
    assert res.json == expected_body
    client.get("/api/v1/user/logout")

    # Test "teacher" role
    expected_body = {"anonymous": True, "user": True, "teacher": True, "admin": False}
    client.post(
        "/api/v1/user/login",
        json={
            "username": TEACHER_DEMOGRAPHICS["username"],
            "password": TEACHER_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    res = client.get("/api/v1/user/authorize/user")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/teacher")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/admin")
    assert res.status_code == 401
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/anonymous")
    assert res.status_code == 200
    assert res.json == expected_body
    client.get("/api/v1/user/logout")

    # Test "admin" role
    expected_body = {"anonymous": True, "user": True, "teacher": True, "admin": True}
    client.post(
        "/api/v1/user/login",
        json={
            "username": ADMIN_DEMOGRAPHICS["username"],
            "password": ADMIN_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    res = client.get("/api/v1/user/authorize/user")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/teacher")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/admin")
    assert res.status_code == 200
    assert res.json == expected_body
    res = client.get("/api/v1/user/authorize/anonymous")
    assert res.status_code == 200
    assert res.json == expected_body
    client.get("/api/v1/user/logout")


def test_disable_account(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the /user/disable_account endpoint."""
    clear_db()
    register_test_accounts()
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    csrf_t = get_csrf_token(res)

    # Attempt to disable account with an incorrect password
    res = client.post(
        "/api/v1/user/disable_account",
        json={"password": "invalid"},
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 422
    assert res.json["message"] == "The provided password is not correct."

    # Successfully disable account
    db = get_conn()
    user_before_disabling = db.users.find_one(
        {"username": STUDENT_DEMOGRAPHICS["username"]}
    )
    assert user_before_disabling["disabled"] is False
    res = client.post(
        "/api/v1/user/disable_account",
        json={"password": STUDENT_DEMOGRAPHICS["password"]},
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True
    user_after_disabling = db.users.find_one(
        {"username": STUDENT_DEMOGRAPHICS["username"]}
    )
    assert user_after_disabling["disabled"] is True


def test_update_password(mongo_proc, redis_proc, client):  # noqa (fixture)
    clear_db()
    register_test_accounts()
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    csrf_t = get_csrf_token(res)

    # Attempt to update password with incorrect current password
    res = client.post(
        "/api/v1/user/update_password",
        json={
            "current_password": "invalid",
            "new_password": "newpassword",
            "new_password_confirmation": "newpassword",
        },
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 422
    assert res.json["message"] == "Your current password is incorrect."

    # Attempt to update password but the passwords don't match
    res = client.post(
        "/api/v1/user/update_password",
        json={
            "current_password": STUDENT_DEMOGRAPHICS["password"],
            "new_password": "newpassword1",
            "new_password_confirmation": "newpassword2",
        },
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 422
    assert res.json["message"] == "Your passwords do not match."

    # Successfully update password and log in
    res = client.post(
        "/api/v1/user/update_password",
        json={
            "current_password": STUDENT_DEMOGRAPHICS["password"],
            "new_password": "newpassword",
            "new_password_confirmation": "newpassword",
        },
        headers=[("X-CSRF-Token", csrf_t), ("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True

    client.get("/api/v1/user/logout")
    res = client.post(
        "/api/v1/user/login",
        json={"username": STUDENT_DEMOGRAPHICS["username"], "password": "newpassword"},
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True


def test_get_user(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the GET /user endpoint."""
    clear_db()
    register_test_accounts()

    # Test without logging in
    res = client.get("/api/v1/user")
    assert res.status_code == 200
    assert res.json == {"logged_in": False}

    # Test after logging in
    client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )

    expected_body = {
        "admin": False,
        "completed_minigames": [],
        "extdata": {},
        "logged_in": True,
        "score": 0,
        "teacher": False,
        "tokens": 0,
        "unlocked_walkthroughs": [],
        "username": STUDENT_DEMOGRAPHICS["username"],
        "verified": True,
    }
    res = client.get("/api/v1/user")
    assert res.status_code == 200
    for k, v in res.json.items():
        if k not in {"uid", "tid"}:
            assert res.json[k] == expected_body[k]


def test_patch_user(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the PATCH /user endpoint."""
    clear_db()
    register_test_accounts()
    res = client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    csrf_t = get_csrf_token(res)

    updated_extdata = {"testdata": "1"}
    res = client.patch(
        "/api/v1/user",
        json={"extdata": updated_extdata},
        headers=[("X-CSRF-Token", csrf_t)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True

    res = client.get("api/v1/user")
    assert res.json["extdata"] == updated_extdata


def test_reset_password(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the password reset endpoints."""
    clear_db()
    register_test_accounts()

    # App init will set api.email.mail to a testing FlaskMail instance
    with api.email.mail.record_messages() as outbox:

        # Send the password reset request
        res = client.post(
            "/api/v1/user/reset_password/request",
            json={"username": STUDENT_DEMOGRAPHICS["username"],},
            headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
        )
        assert res.status_code == 200
        assert res.json["success"] is True

        # Verify that the token is in the DB
        # Since we cleared the DB, it's the only token in there, so
        # we can avoid searching for it...
        db = get_conn()
        db_token = db.get_collection("tokens").find_one({})["tokens"]["password_reset"]
        assert db_token is not None

        # Verify that the email is in the outbox
        assert len(outbox) == 1
        assert outbox[0].subject == "CTF Placeholder Password Reset"
        assert db_token in outbox[0].body

    # Attempt to confirm the reset with the wrong token
    res = client.post(
        "/api/v1/user/reset_password",
        json={
            "reset_token": "wrongtoken",
            "new_password": "newpassword",
            "new_password_confirmation": "newpassword",
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 422
    assert res.json["message"] == "Invalid password reset token"

    # Perform the password reset with the correct token
    res = client.post(
        "/api/v1/user/reset_password",
        json={
            "reset_token": db_token,
            "new_password": "newpassword",
            "new_password_confirmation": "newpassword",
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True

    # Log in with the new password
    client.get("/api/v1/user/logout")
    res = client.post(
        "/api/v1/user/login",
        json={"username": STUDENT_DEMOGRAPHICS["username"], "password": "newpassword",},
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )
    assert res.status_code == 200
    assert res.json["success"] is True


def test_verify(mongo_proc, redis_proc, client):  # noqa (fixture)
    """Tests the /user/verify endpoint."""
    clear_db()
    register_test_accounts()
    client.post(
        "/api/v1/user/login",
        json={
            "username": STUDENT_DEMOGRAPHICS["username"],
            "password": STUDENT_DEMOGRAPHICS["password"],
        },
        headers=[("Limit-Bypass", RATE_LIMIT_BYPASS_KEY)],
    )

    # Force user to unverified status and set a token
    db = get_conn()
    test_user = db.users.find_one_and_update(
        {"username": STUDENT_DEMOGRAPHICS["username"]}, {"$set": {"verified": False}}
    )
    db.tokens.insert(
        {
            "uid": test_user["uid"],
            "email_verification_count": 1,
            "tokens": {"email_verification": "test_token"},
        }
    )

    # Attempt to verify with an incorrect token
    res = client.get(
        "/api/v1/user/verify?uid={}&token=invalid".format(test_user["uid"])
    )
    assert res.status_code == 302
    assert res.headers["Location"] == "http://192.168.2.2/#status=verification_error"

    test_user = db.users.find_one({"username": STUDENT_DEMOGRAPHICS["username"]})
    assert test_user["verified"] is False

    # Successfully verify user
    res = client.get(
        "/api/v1/user/verify?uid={}&token=test_token".format(test_user["uid"])
    )
    assert res.status_code == 302
    assert res.headers["Location"] == "http://192.168.2.2/#status=verified"

    test_user = db.users.find_one({"username": STUDENT_DEMOGRAPHICS["username"]})
    assert test_user["verified"] is True

    # Check that the token has been deleted from the database
    user_tokens = db.tokens.find_one({"uid": test_user["uid"]})
    assert len(user_tokens["tokens"]) == 0
