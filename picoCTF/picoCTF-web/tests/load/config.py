"""Configuration values and common functions for load testing."""

from pymongo import MongoClient

db = None
db_conf = {
    "MONGO_HOST": "127.0.0.1",
    "MONGO_PORT": 27017,
    "MONGO_USER": None,
    "MONGO_PASS": None,
    "MONGO_DB_NAME": "picoCTF-load-testing",
}

API_BASE_URL = "api/v1"
CREATE_GROUP_ENDPOINT = API_BASE_URL + "/groups"
CREATE_TEAM_ENDPOINT = API_BASE_URL + "/teams"
FEEDBACK_ENDPOINT = API_BASE_URL + "/feedback"
GROUPS_ENDPOINT = API_BASE_URL + "/groups"
JOIN_GROUP_ENDPOINT = API_BASE_URL + "/team/join_group"
JOIN_TEAM_ENDPOINT = API_BASE_URL + "/team/join"
LOGIN_ENDPOINT = API_BASE_URL + "/user/login"
LOGOUT_ENDPOINT = API_BASE_URL + "/user/logout"
PROBLEMS_ENDPOINT = API_BASE_URL + "/problems"
REGISTRATION_ENDPOINT = API_BASE_URL + "/users"
REGISTRATION_STATS_ENDPOINT = API_BASE_URL + "/stats/registration"
SCOREBOARDS_ENDPOINT = API_BASE_URL + "/scoreboards"
SETTINGS_ENDPOINT = API_BASE_URL + "/settings"
SHELL_SERVERS_ENDPOINT = API_BASE_URL + "/shell_servers"
STATUS_ENDPOINT = API_BASE_URL + "/status"
SUBMISSIONS_ENDPOINT = API_BASE_URL + "/submissions"
TEAM_ENDPOINT = API_BASE_URL + "/team"
TEAM_SCORE_ENDPOINT = API_BASE_URL + "/team/score"
TEAM_SCORE_PROGRESSION_ENDPOINT = API_BASE_URL + "/team/score_progression"
USER_DELETE_ACCOUNT_ENDPOINT = API_BASE_URL + "/user/disable_account"
USER_ENDPOINT = API_BASE_URL + "/user"
USER_EXPORT_ENDPOINT = API_BASE_URL + "/user/export"
USER_PASSWORD_CHANGE_ENDPOINT = API_BASE_URL + "/user/update_password"

CLASSROOM_PAGE_URL = "classroom"
GAME_PAGE_URL = "game"
NEWS_PAGE_URL = "news"
PROBLEMS_PAGE_URL = "problems"
PROFILE_PAGE_URL = "profile"
SCOREBOARD_PAGE_URL = "scoreboard"
SHELL_PAGE_URL = "shell"

MAX_TEAM_SIZE = 5
GROUP_LIMIT = 20

BATCH_REGISTRATION_CSV_FILENAME = "batch_reg_testing.csv"

# Need credentials of a platform admin to retrieve problem flags
ADMIN_USERNAME = "adminuser"
ADMIN_PASSWORD = "adminpw"


def get_db():
    """Retrieve a MongoDB client using the settings in db_conf."""
    global db
    if not db:
        if db_conf["MONGO_USER"] or db_conf["MONGO_PASS"]:
            mongo_client = MongoClient(
                "mongodb://{}:{}@{}:{}/{}?authMechanism=SCRAM-SHA-1".format(
                    db_conf["MONGO_USER"],
                    db_conf["MONGO_PASS"],
                    db_conf["MONGO_HOST"],
                    db_conf["MONGO_PORT"],
                    db_conf["MONGO_DB_NAME"],
                )
            )
        else:
            mongo_client = MongoClient(
                "mongodb://{}:{}/{}".format(
                    db_conf["MONGO_HOST"],
                    db_conf["MONGO_PORT"],
                    db_conf["MONGO_DB_NAME"],
                )
            )
        db = mongo_client[db_conf["MONGO_DB_NAME"]]
    return db
