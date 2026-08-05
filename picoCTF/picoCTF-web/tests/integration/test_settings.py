"""Tests for the /api/v1/settings endpoint."""
from pytest_mongo import factories
from pytest_redis import factories
from .common import (  # noqa (fixture)
    clear_db,
    client,
)


def test_settings(mongo_proc, redis_proc, client):  # noqa
    """Test the /settings endpoint when not logged in as admin."""
    # @TODO currently only tests the default values of these fields
    #       try modifying the settings and testing also
    clear_db()

    expected_responses = {
        "enable_feedback": True,
        "enable_captcha": False,
        "reCAPTCHA_public_key": "",
        "email_verification": False,
        "max_team_size": 5,
        "email_filter": [],
    }
    res = client.get("/api/v1/settings")
    assert res.status_code == 200
    for k, v in expected_responses.items():
        assert res.json[k] == v
