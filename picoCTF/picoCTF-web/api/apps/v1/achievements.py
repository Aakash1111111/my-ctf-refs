"""Achievement management."""
from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import PicoException, require_admin

from .schemas import achievement_patch_req, achievement_req

ns = Namespace("achievements", description="Achievement management")


@ns.route("")
class AchievementList(Resource):
    """Get the full list of achievements, or add a new achievement."""

    @require_admin
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def get(self):
        """Get the full list of achievements."""
        return api.achievement.get_all_achievements(), 200

    @require_admin
    @ns.expect(achievement_req)
    @ns.response(201, "Achievement added")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def post(self):
        """Add a new achievement."""
        req = achievement_req.parse_args(strict=True)
        aid = api.achievement.insert_achievement(**req)
        res = jsonify({"success": True, "aid": aid})
        res.status_code = 201
        return res


@ns.response(200, "Success")
@ns.response(404, "Achievement not found")
@ns.route("/<string:achievement_id>")
class Achievement(Resource):
    """Get or update a specific achievement."""

    @require_admin
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def get(self, achievement_id):
        """Retrieve a specific achievement."""
        res = api.achievement.get_achievement(achievement_id)
        if not res:
            raise PicoException("Achievement not found", status_code=404)
        else:
            return res, 200

    @require_admin
    @ns.expect(achievement_req)
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def put(self, achievement_id):
        """Replace an existing achievement."""
        req = achievement_req.parse_args(strict=True)
        aid = api.achievement.update_achievement(achievement_id, req)
        if aid is None:
            raise PicoException("Achievement not found", status_code=404)
        return jsonify({"success": True, "aid": aid})

    @require_admin
    @ns.expect(achievement_patch_req)
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def patch(self, achievement_id):
        """Update an existing achievement."""
        req = {
            k: v for k, v in achievement_patch_req.parse_args().items() if v is not None
        }
        aid = api.achievement.update_achievement(achievement_id, req)
        if aid is None:
            raise PicoException("Achievement not found", status_code=404)
        return jsonify({"success": True, "aid": aid})
