"""Endpoints for getting statistical reports."""
import api
from api import require_admin
from flask import jsonify
from flask_restplus import Namespace, Resource

ns = Namespace("stats", "Statistical aggregations and reports")


@ns.route("/registration")
class RegistrationStatus(Resource):
    """Get information on user, team, and group registrations."""

    def get(self):
        """Get information on user, team, and group registrations."""
        return jsonify(api.stats.get_registration_count())


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.route("/submissions")
class SubmissionStatistics(Resource):
    """View submission statistics, broken down by problem."""

    @require_admin
    def get(self):
        """Get submission statistics, broken down by problem name."""
        return jsonify(
            {
                p["name"]: api.stats.get_problem_submission_stats(p["pid"])
                for p in api.problem.get_all_problems(show_disabled=True)
            }
        )


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.route("/demographics")
class DemographicInformation(Resource):
    """Get demographic information used in analytics."""

    @require_admin
    def get(self):
        """Get demographic information used in analytics."""
        return jsonify(api.stats.get_demographic_data())
