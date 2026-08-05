"""Scoreboard management."""

import api
from api import block_before_competition, PicoException, require_admin
from flask import jsonify
from flask_restplus import Namespace, Resource

from .schemas import score_progressions_req, scoreboard_page_req, scoreboard_req

ns = Namespace("scoreboards", description="Scoreboard management")


@ns.route("")
class ScoreboardList(Resource):
    """Get the list of all scoreboards, or add a new scoreboard."""

    @ns.response(200, "Success")
    def get(self):
        """Get the list of all scoreboards."""
        return jsonify(api.scoreboards.get_all_scoreboards())

    @require_admin
    @ns.response(201, "Scoreboard added")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Permission denied")
    @ns.expect(scoreboard_req)
    def post(self):
        """Add a new scoreboard."""
        req = scoreboard_req.parse_args(strict=True)
        sid = api.scoreboards.add_scoreboard(
            req["name"],
            eligibility_conditions=req["eligibility_conditions"],
            priority=req["priority"],
            sponsor=req["sponsor"],
            logo=req["logo"],
        )
        res = jsonify({"success": True, "sid": sid})
        res.status_code = 201
        return res


@ns.route("/<string:scoreboard_id>")
class Scoreboard(Resource):
    """Get a specific scoreboard."""

    @ns.response(200, "Success")
    @ns.response(404, "Scoreboard not found")
    def get(self, scoreboard_id):
        """Get a specific scoreboard."""
        scoreboard = api.scoreboards.get_scoreboard(scoreboard_id)
        if not scoreboard:
            raise PicoException("Scoreboard not found", 404)
        return jsonify(scoreboard)


@ns.route("/<string:scoreboard_id>/scoreboard")
class ScoreboardPage(Resource):
    """
    Get a results page for an scoreboard.

    If a page is not specified, will attempt to return the page containing the
    current team, falling back to the first page if neccessary.
    """

    @ns.response(200, "Success")
    @ns.response(404, "Scoreboard not found")
    @ns.response(422, "Competition has not started")
    @ns.expect(scoreboard_page_req)
    def get(self, scoreboard_id):
        """Retrieve a scoreboard page for a scoreboard."""
        req = scoreboard_page_req.parse_args(strict=True)
        scoreboard = api.scoreboards.get_scoreboard(scoreboard_id)
        if not scoreboard:
            raise PicoException("Scoreboard not found", 404)
        if req["search"] is not None:
            page = api.stats.get_filtered_scoreboard_page(
                {"scoreboard_id": scoreboard_id}, req["search"], req["page"] or 1
            )
        else:
            page = api.stats.get_scoreboard_page(
                {"scoreboard_id": scoreboard_id}, req["page"]
            )
        return jsonify(
            {"scoreboard": page[0], "current_page": page[1], "total_pages": page[2]}
        )


@ns.route("/<string:scoreboard_id>/score_progressions")
class ScoreProgressionsResult(Resource):
    """Get a list of score progressions for the top n teams on a scoreboard."""

    @ns.response(200, "Success")
    @ns.response(403, "Must be admin to specify limit")
    @ns.response(404, "Scoreboard not found")
    @ns.response(422, "Competition has not started")
    @ns.expect(score_progressions_req)
    def get(self, scoreboard_id):
        """Get a list of teams' score progressions."""
        req = score_progressions_req.parse_args(strict=True)
        scoreboard = api.scoreboards.get_scoreboard(scoreboard_id)
        if not scoreboard:
            raise PicoException("Scoreboard not found", 404)
        if req["limit"] and (
            not api.user.is_logged_in() or not api.user.get_user()["admin"]
        ):
            raise PicoException("Must be admin to specify limit", 403)
        return jsonify(
            api.stats.get_top_teams_score_progressions(
                limit=(req["limit"] or 5), scoreboard_id=scoreboard_id
            )
        )
