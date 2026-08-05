"""Module for handling problem feedback."""

from datetime import datetime

from voluptuous import Length, Required, Schema

import api
from api import check, log_action, PicoException, validate

feedback_schema = Schema(
    {
        Required("liked"): check(
            ("liked must be a boolean", [lambda x: type(x) == bool])
        ),
        "comment": check(
            ("The comment must be no more than 500 characters", [str, Length(max=500)])
        ),
        "timeSpent": check(("Time spend must be a number", [int])),
        "source": check(
            ("The source must be no more than 500 characters", [str, Length(max=10)])
        ),
    }
)


def get_problem_feedback(pid=None, tid=None, uid=None, count_only=False):
    """
    Retrieve feedback for a given problem, team, or user.

    Args:
        pid: the problem id
        tid: the team id
        uid: the user id
        count_only: only sums likes dislikes instead of full feedback entries
    Returns:
        A list of problem feedback entries.
    """
    db = api.db.get_conn()
    match = {}

    if pid is not None:
        match.update({"pid": pid})
    if tid is not None:
        match.update({"tid": tid})
    if uid is not None:
        match.update({"uid": uid})
    if count_only:
        likes = {"feedback.liked": True}
        likes.update(match)
        dislikes = {"feedback.liked": False}
        dislikes.update(match)
        return {
            "likes": db.problem_feedback.count_documents(likes),
            "dislikes": db.problem_feedback.count_documents(dislikes),
        }
    else:
        return list(db.problem_feedback.find(match, {"_id": 0}))


@log_action
def upsert_feedback(pid, feedback):
    """
    Add or update problem feedback in the database.

    Args:
        pid: the problem id
        feedback: the problem feedback.
    Raises:
        PicoException if provided pid does not exist

    """
    db = api.db.get_conn()

    uid = api.user.get_user()["uid"]

    # Make sure the problem actually exists.
    if not api.problem.get_problem(pid, {"pid": 1}):
        raise PicoException("Problem not found", 404)

    team = api.user.get_team(uid=uid)
    solved = pid in api.problem.get_solved_pids(tid=team["tid"])

    validate(feedback_schema, feedback)

    # update feedback if already present
    if get_problem_feedback(pid=pid, uid=uid) != []:
        db.problem_feedback.update(
            {"pid": pid, "uid": uid},
            {"$set": {"timestamp": datetime.utcnow(), "feedback": feedback}},
        )
    else:
        db.problem_feedback.insert(
            {
                "pid": pid,
                "uid": uid,
                "tid": team["tid"],
                "solved": solved,
                "timestamp": datetime.utcnow(),
                "feedback": feedback,
            }
        )

        # @TODO achievement processing needs to be fixed/reviewed
        # api.achievement.process_achievements("review", {
        #     "uid": uid,
        #     "tid": team['tid'],
        #     "pid": pid
        # })
