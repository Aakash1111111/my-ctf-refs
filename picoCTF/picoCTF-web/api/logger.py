"""Manage loggers for the API."""
import inspect
import logging
import logging.handlers
import traceback
from datetime import datetime
from functools import wraps

import pymongo
from flask import has_request_context
from flask import logging as flask_logging
from flask import request

import api

critical_error_timeout = 600
log = logging.getLogger(__name__)


class FunctionLoggingHandler(logging.StreamHandler):
    """
    Logs function invocations into the database.

    Used by the @log_action decorator.
    """

    def __init__(self):
        """Initialize the logger."""
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        """Store record into the db."""
        information = get_request_information()
        result = record.msg

        if type(result) == dict:

            information.update(
                {
                    "event": result["name"],
                    "args": result["args"],
                    "time": datetime.now(),
                }
            )

            if "exception" in result:
                information["success"] = False
                information["exception"] = repr(result["exception"])
            elif "result" in result:
                information["success"] = True
                information["result"] = repr(result["result"])

            api.db.get_conn().statistics.insert(information)


class ExceptionHandler(logging.StreamHandler):
    """Logs exceptions into the database."""

    def __init__(self):
        """Initialize the logger."""
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        """Store record into the db."""
        information = get_request_information()

        information.update(
            {
                "id": api.common.token(),
                "time": datetime.now(),
                "message": record.msg,
                "trace": traceback.format_exc(),
                "visible": True,
            }
        )
        api.db.get_conn().exceptions.insert(information)


def get_request_information():
    """
    Return a dictionary of information about the user at the time of logging.

    Returns:
        The dictionary.

    """
    information = {}

    if has_request_context():
        information["request"] = {
            "api_endpoint_method": request.method,
            "api_endpoint": request.path,
            "ip": request.remote_addr,
            "platform": request.user_agent.platform,
            "browser": request.user_agent.browser,
            "browser_version": request.user_agent.version,
            "user_agent": request.user_agent.string,
        }

        if api.user.is_logged_in():
            user = api.user.get_user()
            team = api.user.get_team()
            groups = api.team.get_groups(user["tid"])

            information["user"] = {
                "username": user["username"],
                "email": user["email"],
                "team_name": team["team_name"],
                "groups": [group["name"] for group in groups],
            }
    return information


def setup_logs(args):
    """
    Initialize the api loggers.

    Args:
        args: dict containing the configuration options.
    """
    flask_logging.create_logger = lambda app: logging.getLogger(app.logger_name)

    logger = logging.getLogger("werkzeug")
    if logger:
        logger.setLevel(logging.ERROR)

    level = [logging.WARNING, logging.INFO, logging.DEBUG][
        min(args.get("verbose", 1), 2)
    ]

    # Handle ERROR level with ExceptionHandler
    internal_error_log = ExceptionHandler()
    internal_error_log.setLevel(logging.ERROR)
    log.root.setLevel(level)
    log.root.addHandler(internal_error_log)

    # Handle INFO level with FunctionLoggingHandler
    stats_log = FunctionLoggingHandler()
    stats_log.setLevel(logging.INFO)
    log.root.addHandler(stats_log)

def _remove_parameter(arg_dict, param_path):
    """Recurses through a dictionary of dictionaries and removes the given param"""
    if param_path[0] not in arg_dict:
        return arg_dict


    new_dict = arg_dict.copy() # Needed to avoid aliasing effects
    if len(param_path) == 1:
        new_dict[param_path[0]] = "REDACTED"
        return new_dict

    new_dict[param_path[0]] = _remove_parameter(arg_dict[param_path[0]], param_path[1:])
    return new_dict

def log_action(_f=None, dont_log=[]):
    """Log a function invocation and its result."""
    def outer_wrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            """Provide contextual information to the logger."""

            func_sig = inspect.signature(f)
            func_args = dict(func_sig.bind_partial(*args, **kwargs).arguments)
            for param in dont_log:
                param_path = param.split(".")
                func_args = _remove_parameter(func_args, param_path)
            log_information = {
                "name": "{}.{}".format(f.__module__, f.__name__),
                "args": func_args,
                "result": None,
            }
            try:
                log_information["result"] = f(*args, **kwargs)
            except Exception as error:
                log_information["exception"] = error
                raise error
            finally:
                log.info(log_information)
            return log_information["result"]

        return wrapper

    if _f is None:
        return outer_wrapper
    else:
        return outer_wrapper(_f)


def get_api_exceptions(result_limit=50):
    """
    Retrieve the most recent logged exceptions.

    Args:
        result_limit: the maximum number of exceptions to return.

    Returns:
        list of exception dicts

    """
    db = api.db.get_conn()
    results = (
        db.exceptions.find({"visible": True}, {"_id": 0})
        .sort([("time", pymongo.DESCENDING)])
        .limit(result_limit)
    )
    return list(results)


def get_api_exception(exception_id):
    """
    Retrieve a specific exception.

    Args:
        exception_id: ID of the exception to retrieve.

    Returns:
        the specified exception dict, or None if not found

    """
    db = api.db.get_conn()
    return db.exceptions.find_one({"id": exception_id}, {"_id": 0})


def dismiss_api_exceptions(exception_id=None):
    """
    Dismiss logged exceptions.

    Args:
        id (optional): ID of the exception to dismiss. If not provided,
                       dismisses all logged exceptions.

    Returns:
        the number of dismissed exceptions

    """
    db = api.db.get_conn()
    match = {}
    if exception_id:
        match["id"] = exception_id
    res = db.exceptions.update_many(match, {"$set": {"visible": False}})
    return res.modified_count
