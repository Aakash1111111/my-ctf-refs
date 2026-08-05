"""
Problem related endpoints.

Problems and bundles are not treated as usual CRUD resources because
the source of truth for problem and bundle state is the shell server(s).

So bundles and problems are essentially treated as read-only, with the
exception of the PATCH /problems endpoint, which takes a shell server's
output and updates the state of the problems and bundles accordingly.

There are two other exceptions to this:
- A problem's "disabled" property is a web API-only concept. The shell server
  will continue to serve the problem either way.
- A bundle's "dependencies_enabled" property works similarly.

These two properties are the ONLY fields modifiable via PATCH reqests on
problem or bundle resources, respectively.

Note that bundles, despite their name, are really just documents specifying
unlock requirements for existing problems.
"""
from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import block_before_competition, PicoException, require_admin, require_login

from .schemas import problem_patch_req, problems_req, shell_server_out

ns = Namespace("problems", description="Problem management")


@ns.response(400, "Error parsing request")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.route("")
class ProblemList(Resource):
    """Get the list of problems, or update the problem/bundle state."""

    @block_before_competition
    @require_login
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Unauthorized")
    @ns.response(422, "Competition has not started")
    @ns.expect(problems_req)
    def get(self):
        """
        Get the list of problems, with optional filtering.

        By default, only problems unlocked by your team will be displayed.
        Teachers or admins can override this by specifying
        '?unlocked_only=false'. However, teachers will only recieve problems'
        names, categories, and scores when doing this.
        """
        req = problems_req.parse_args(strict=True)

        # Handle the 'category' arg if present but unset
        if req["category"] == "":
            req["category"] = None

        # To begin, get all problems, filtered by category and include_disabled
        problems = api.problem.get_all_problems(
            category=req["category"], show_disabled=req["include_disabled"]
        )

        # Add the unlocked, solved, review, and container fields
        curr_user = api.user.get_user()
        for problem in problems:
            pid = problem["pid"]
            tid = curr_user["tid"]
            problem["solves"] = api.stats.get_problem_solves(pid)
            problem["unlocked"] = pid in api.problem.get_unlocked_pids(tid)
            problem["solved"] = pid in api.problem.get_solved_pids(tid=tid)
            if curr_user.get("admin", False):
                problem["reviews"] = api.problem_feedback.get_problem_feedback(
                    pid=pid, count_only=True
                )
            containers = api.docker.submission_to_cid(tid, pid)
            if containers.count() > 0:
                problem["container"] = dict(containers.next())

        # Handle the solved_only param
        if req["solved_only"]:
            problems = [p for p in problems if (p["solved"] is True)]

        # Handle the unlocked_only param, which depends on user role
        # Unless just getting the count - then normal users allowed
        is_teacher = api.user.get_user().get("teacher", False)
        is_admin = api.user.get_user().get("admin", False)
        if req["unlocked_only"] is False:
            if req["count_only"] is False and not is_teacher and not is_admin:
                raise PicoException(
                    "You must be a teacher or admin to use " + "unlocked_only=false.",
                    status_code=403,
                )
            if not is_admin:
                # Teachers recieve only a reduced subset of fields
                # when getting all problems.
                problems = [
                    {"name": p["name"], "category": p["category"], "score": p["score"]}
                    for p in problems
                ]
        else:
            # When unlocked_only is True (by default), strip out any problems
            # that have not been unlocked by the current user's team.
            problems = [p for p in problems if (p["unlocked"] is True)]
            # Additionally, show only fields from the assigned instance.
            problems = [
                api.problem.filter_problem_instances(p, api.user.get_user()["tid"])
                for p in problems
            ]
            # Strip out admin-only fields
            problems = api.problem.sanitize_problem_data(problems)

        # Handle the count_only param
        if req["count_only"]:
            return jsonify({"count": len(problems)})
        else:
            return jsonify(problems)

    @require_admin
    @ns.expect(shell_server_out)
    @ns.response(200, "Problem list updated")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.response(404, "Shell server not found")
    def patch(self):
        """
        Update the problem and bundle state via shell server output.

        If `shell_manager publish` output is not provided as a payload,
        will attempt to automatically request it from the provided
        shell server.

        Note that this will only add new / update existing problems – if a
        problem has been removed from the shell server, it should be
        disabled using the PATCH /<problem_id> endpoint or manually
        removed from the database.
        """
        req = {
            k: v
            for k, v in shell_server_out.parse_args(strict=True).items()
            if v is not None
        }
        # Check that the provided sid is valid
        found = api.shell_servers.get_server(req["sid"])
        if found is None:
            raise PicoException("Shell server not found", status_code=404)
        if "problems" in req:
            api.problem.load_published(
                {
                    "problems": req["problems"],
                    "bundles": req["bundles"],
                    "sid": req["sid"],
                }
            )
        else:
            output = api.shell_servers.get_publish_output(req["sid"])
            api.problem.load_published(
                {
                    "problems": output["problems"],
                    "bundles": output["bundles"],
                    "sid": req["sid"],
                }
            )

        return jsonify({"success": True})


@require_login
@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Problem not found")
@ns.route("/<string:problem_id>")
class Problem(Resource):
    """Get or update the availability of a specific problem."""

    def get(self, problem_id):
        """Retrieve a specific problem."""
        # Ensure that the problem exists
        problem = api.problem.get_problem(problem_id)
        if not problem:
            raise PicoException("Problem not found", status_code=404)

        # Add synthetic fields
        curr_user = api.user.get_user()
        problem["solves"] = api.stats.get_problem_solves(problem["pid"])
        problem["unlocked"] = problem["pid"] in api.problem.get_unlocked_pids(
            curr_user["tid"]
        )
        problem["solved"] = problem["pid"] in api.problem.get_solved_pids(
            tid=curr_user["tid"]
        )
        if curr_user.get("admin", False):
            problem["reviews"] = api.problem_feedback.get_problem_feedback(
                pid=problem["pid"], count_only=True
            )

        # Ensure that the user has unlocked it
        if not problem["unlocked"]:
            raise PicoException("You have not unlocked this problem", 403)

        # Strip out instance and system info if not admin
        curr_user = api.user.get_user()
        if not curr_user.get("admin", False):
            problem = api.problem.filter_problem_instances(problem, curr_user["tid"])
            problem = api.problem.sanitize_problem_data(problem)

        return jsonify(problem)

    @require_admin
    @ns.response(200, "Success")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.expect(problem_patch_req)
    def patch(self, problem_id):
        """
        Update a specific problem.

        The only valid field for this method is "disabled".
        Other fields are pulled from the shell server, and
        can be updated via the PATCH /problems endpoint.
        """
        req = problem_patch_req.parse_args(strict=True)
        pid = api.problem.set_problem_availability(problem_id, req["disabled"])
        if not pid:
            raise PicoException("Problem not found", status_code=404)
        else:
            return jsonify({"success": True})


@ns.route("/<string:problem_id>/walkthrough")
class ProblemWalkthrough(Resource):
    """Get the walkthrough for a problem, if unlocked."""

    @block_before_competition
    @require_login
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Walkthrough not unlocked")
    @ns.response(404, "Problem or walkthrough not found")
    @ns.response(422, "Competition has not started")
    def get(self, problem_id):
        """Get the walkthrough for a problem, if unlocked."""
        uid = api.user.get_user()["uid"]
        problem = api.problem.get_problem(problem_id, {"pid": 1, "walkthrough": 1})
        if problem is None:
            raise PicoException("Problem not found", 404)
        if problem.get("walkthrough", None) is None:
            raise PicoException(
                "This problem does not have a walkthrough!", status_code=404
            )
        if problem["pid"] not in api.problem.get_unlocked_walkthroughs(uid):
            raise PicoException(
                "You haven't unlocked this walkthrough yet!", status_code=403
            )
        return jsonify({"walkthrough": problem["walkthrough"]})


@ns.route("/<string:problem_id>/walkthrough/unlock")
class ProblemWalkthroughUnlockResponse(Resource):
    """Spend tokens to unlock the walkthrough for a problem."""

    @block_before_competition
    @require_login
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(404, "Problem or walkthrough not found")
    @ns.response(422, "Insufficient tokens or competition has not started")
    def get(self, problem_id):
        """Spend tokens to unlock the walkthrough for a problem."""
        curr_user = api.user.get_user()
        problem = api.problem.get_problem(problem_id, {"score": 1, "walkthrough": 1})
        if problem is None:
            raise PicoException("Problem not found", 404)
        if problem.get("walkthrough", None) is None:
            raise PicoException(
                "This problem does not have a walkthrough!", status_code=404
            )
        if curr_user.get("tokens", 0) >= problem["score"]:
            api.problem.unlock_walkthrough(
                curr_user["uid"], problem_id, problem["score"]
            )
            return jsonify({"success": True})
        else:
            raise PicoException(
                "You do not have enough tokens to unlock this walkthrough!",
                status_code=422,
            )
