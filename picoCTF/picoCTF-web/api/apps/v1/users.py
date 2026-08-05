"""User management endpoints."""
import re
import string

from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import PicoException, rate_limit, require_admin

from .schemas import user_req, user_delete_req, user_search_req

ns = Namespace("users", description="User management")


@ns.route("")
class UserList(Resource):
    """Get the full list of users, or add a new user."""

    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @require_admin
    def get(self):
        """Get the full list of users."""
        return jsonify(api.user.get_all_users())

    @rate_limit(limit=5, duration=15, by_ip=True)
    @ns.response(201, "Successfully created user")
    @ns.response(400, "Error parsing request")
    @ns.response(409, "Username not available")
    @ns.response(429, "Too many requests, slow down!")
    @ns.expect(user_req)
    def post(self):
        """Register a new user."""
        req = user_req.parse_args(strict=True)

        # Do additional validation on request, due to RequestParser
        # limitations (@TODO handle w/ Marshmallow)
        if "age" not in req["demo"] or req["demo"]["age"] not in ["13-17", "18+"]:
            raise PicoException(
                "'age' must be specified in the 'demo' object. Valid values "
                + "are: ['13-17', '18+']",
                status_code=400,
            )
        if (
            api.config.get_settings()["email"]["parent_verification_email"]
            and req["demo"]["age"] != "18+"
            and (
                "parentemail" not in req["demo"]
                or not re.match(r".+@.+\..{2,}", req["demo"]["parentemail"])
            )
        ):
            raise PicoException(
                "Must provide a valid parent email address under the key "
                + "'demo.parentemail'.",
                status_code=400,
            )
        accepted_genders = ["male", "female", "nb/gf", "nl/no"]
        if "gender" in req["demo"] and req["demo"]["gender"] not in accepted_genders:
            raise PicoException(
                f"'demo.gender' must be one of: {str(accepted_genders)}", 400
            )
        if not all(
            [
                c in string.digits + string.ascii_lowercase
                for c in req["username"].lower()
            ]
        ):
            raise PicoException("Usernames must be alphanumeric.", status_code=400)

        # Clean up input data
        req["affiliation"] = req["affiliation"].strip()

        # Attempt to create the user
        uid = api.user.add_user(req)

        res = jsonify({"success": True, "uid": uid})
        res.status_code = 201
        return res


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "User not found")
@ns.route("/<string:user_id>")
class User(Resource):
    """Get a specific user."""

    @require_admin
    def get(self, user_id):
        """Retrieve a specific user."""
        res = api.user.get_user(uid=user_id)
        if not res:
            raise PicoException("User not found", status_code=404)
        return res, 200


@ns.route("/<string:user_id>/delete")
class UserDeleteResponse(Resource):
    """Delete a specific user with an optional reason"""

    @require_admin
    @ns.expect(user_delete_req)
    def post(self, user_id):
        """Disable a specific user."""
        req = user_delete_req.parse_args(strict=True)
        user = api.user.get_user(uid=user_id)
        if not user:
            raise PicoException("User not found", status_code=404)
        api.user.disable_account(user_id, req["reason"])
        return jsonify({"success": True})


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "User not found")
@ns.route("/<string:user_id>/export")
class UserDataExport(Resource):
    """Export all data of a given user."""

    @require_admin
    def get(self, user_id):
        """Export all data of a given user."""
        user_data = api.user.get_user(uid=user_id)
        if not user_data:
            raise PicoException("User not found", status_code=404)
        submissions = api.submissions.get_submissions(uid=user_id)
        feedbacks = api.problem_feedback.get_problem_feedback(uid=user_id)
        return jsonify(
            {"user": user_data, "submissions": submissions, "feedback": feedbacks}
        )


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "User not found")
@ns.route("/search")
class UserSearch(Resource):
    """Search for a given user."""

    @require_admin
    @ns.expect(user_search_req)
    def post(self):
        """Search for a given user."""
        req = user_search_req.parse_args(strict=True)

        if req["field"] == "Email":
            user_data = api.user.get_users(email=req["query"])
        elif req["field"] == "Parent Email":
            user_data = api.user.get_users(parentemail=req["query"])
        elif req["field"] == "User Name":
            user_data = api.user.get_users(username=req["query"])

        if not user_data:
            raise PicoException("User not found", status_code=404)
        return jsonify(user_data)
