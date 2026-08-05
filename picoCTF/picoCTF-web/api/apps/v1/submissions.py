"""Submission related endpoints."""
from flask import jsonify, request
from flask_restplus import Namespace, Resource

import api
from api import (
    block_after_competition,
    block_before_competition,
    check_csrf,
    rate_limit,
    require_admin,
    require_login,
)

from .schemas import submission_req

ns = Namespace(
    "submissions", description="Submit flags and list " + "submission attempts"
)


@ns.route("")
class SubmissionList(Resource):
    """Submit new solution attempts, or clear all existing submissions."""

    @check_csrf
    @block_after_competition
    @block_before_competition
    @require_login
    @rate_limit(limit=5, duration=30)
    @ns.response(201, "Submission successful")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "CSRF token invalid")
    @ns.response(422, "Problem not unlocked or outside of competition period")
    @ns.response(429, "Too many requests, slow down!")
    @ns.expect(submission_req)
    def post(self):
        """Submit a solution to a problem."""
        user_account = api.user.get_user()
        tid = user_account["tid"]
        uid = user_account["uid"]
        req = submission_req.parse_args(strict=True)
        pid = req["pid"]
        key = req["key"]
        method = req["method"]
        ip = request.remote_addr

        (
            correct,
            previously_solved_by_user,
            previously_solved_by_team,
        ) = api.submissions.submit_key(tid, pid, key, method, uid, ip)

        if correct and not previously_solved_by_team:
            message = "That is correct!"
        elif not correct and not previously_solved_by_team:
            message = "That is incorrect!"
        elif correct and previously_solved_by_user:
            message = (
                "Flag correct: however, you have already solved " + "this problem."
            )
        elif correct and previously_solved_by_team:
            message = (
                "Flag correct: however, your team has already "
                + "received points for this flag."
            )
        elif not correct and previously_solved_by_user:
            message = (
                "Flag incorrect: please note that you have "
                + "already solved this problem."
            )
        elif not correct and previously_solved_by_team:
            message = (
                "Flag incorrect: please note that someone on your "
                + "team has already solved this problem."
            )

        res = jsonify({"correct": correct, "message": message})
        res.status_code = 201
        return res

    @require_admin
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.response(500, "Debug mode not enabled")
    def delete(self):
        """Clear all submissions (debug mode only)."""
        api.submissions.clear_all_submissions()
        return jsonify({"success": True})
