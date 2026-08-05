"""Problem feedback related endpoints."""
from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import (
    block_before_competition,
    check_csrf,
    PicoException,
    require_admin,
    require_login,
)

from .schemas import feedback_list_req, feedback_submission_req

ns = Namespace("feedback", description="List and submit problem feedback")


@ns.route("")
class FeedbackList(Resource):
    """Get the list of problem feedback, or submit new feedback."""

    @block_before_competition
    @require_login
    @ns.response(200, "Success")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.response(422, "Competition has not started")
    def get(self):
        """
        Get the list of your submitted problem feedback.
        """
        raw_feedback = api.problem_feedback.get_problem_feedback(
            uid=api.user.get_user()["uid"]
        )
        return jsonify(
            [{"feedback": f["feedback"], "pid": f["pid"]} for f in raw_feedback]
        )

    @check_csrf
    @block_before_competition
    @require_login
    @ns.response(201, "Feedback accepted")
    @ns.response(400, "Error parsing request")
    @ns.response(403, "CSRF token invalid")
    @ns.response(404, "Problem not found")
    @ns.response(422, "Competition has not started")
    @ns.response(500, "Feedback submissions disabled")
    @ns.expect(feedback_submission_req)
    def post(self):
        """
        Submit problem feedback.

        Will update existing feedback if the current user and provided
        problem ID match a previous submission.
        """
        if not api.config.get_settings()["enable_feedback"]:
            raise PicoException(
                "Problem feedback is not currently being accepted.", status_code=500
            )
        req = feedback_submission_req.parse_args(strict=True)
        api.problem_feedback.upsert_feedback(req["pid"], req["feedback"])
        res = jsonify({"success": True})
        res.status_code = 201
        return res


@ns.route("/all")
class FeedbackList(Resource):
    """Get the list of problem feedback, or submit new feedback."""

    @block_before_competition
    @require_admin
    @require_login
    @ns.response(200, "Success")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.response(422, "Competition has not started")
    @ns.expect(feedback_list_req)
    def get(self):
        """
        Get the list of your submitted problem feedback.

        If called as an admin, returns all submitted feedback, with optional
        filtering using the ?pid, ?uid, and ?tid querystring arguments.
        """
        req = feedback_list_req.parse_args(strict=True)

        # Handle args if they are present but unset
        for arg in ["pid", "uid", "tid"]:
            if req[arg] == "":
                req[arg] = None

        return jsonify(
            api.problem_feedback.get_problem_feedback(
                pid=req["pid"], tid=req["tid"], uid=req["uid"]
            )
        )
