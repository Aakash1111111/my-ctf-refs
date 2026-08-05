"""
Default Flask app startup settings.

Overridable by specifying APP_SETTINGS_FILE.
"""

MONGO_DB_NAME = "ctf"
MONGO_ADDR = "127.0.0.1"
MONGO_PORT = 27017
MONGO_USER = None
MONGO_PW = None
MONGO_REPLICA_SETTINGS = None
MONGO_TLS_SETTINGS = None

REDIS_DB_NUMBER = 0
REDIS_ADDR = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PW = None

RATE_LIMIT_BYPASS_KEY = "INSECURE_DEFAULT_CHANGE_ME"
SECRET_KEY = "INSECURE_DEFAULT_CHANGE_ME"

SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_NAME = "flask"

DOCKER_PUB = None                   # public hostname (e.g. docker.picoctf.com)
DOCKER_HOST = ""                    # internal URI (e.g. tcp://192.168.2.6:2376)
DOCKER_CA = ""                      # path to ca.pem
DOCKER_CLIENT = ""                  # path to cert.pem
DOCKER_KEY = ""                     # path to key.pem
DOCKER_CONTAINERS_PER_TEAM = 3
