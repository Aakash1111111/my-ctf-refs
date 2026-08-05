"""Tests for the /api/v1/status endpoint."""
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
    OTHER_USER_DEMOGRAPHICS,
    load_sample_problems,
    get_conn,
    ensure_within_competition,
    enable_sample_problems,
    get_problem_key,
)


def test_status(mongo_proc, redis_proc, client):  # noqa
    """Test the /status endpoint."""
    # @TODO currently only tests the default values of these fields
    #       try modifying the settings and testing also
    clear_db()

    expected_responses = {
        "competition_active": False,
    }
    nondeterministic_responses = ["time"]
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    for k, v in expected_responses.items():
        assert res.json[k] == v
    for k in nondeterministic_responses:
        assert k in res.json
