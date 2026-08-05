"""Setting related endpoints."""

from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import require_admin

from .schemas import settings_patch_req

ns = Namespace("settings", description="View or modify runtime settings")


@ns.route("")
class Settings(Resource):
    """Get or modify the current settings."""

    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def get(self):
        """Get the current settings. Admins get everything,
        non-admins only get registration/login related params."""
        is_admin = False
        if api.user.is_logged_in():
            is_admin = api.user.get_user().get("admin", False)
        settings = api.config.get_settings()
        if not is_admin:
            return jsonify(
                {
                    "enable_captcha": settings["captcha"]["enable_captcha"],
                    "reCAPTCHA_public_key": settings["captcha"]["reCAPTCHA_public_key"],
                    "email_verification": settings["email"]["email_verification"],
                    "email_filter": settings["email_filter"],
                    "enable_feedback": settings["enable_feedback"],
                    "max_team_size": settings["max_team_size"],
                }
            )
        else:
            return jsonify(settings)

    @require_admin
    @ns.response(200, "Success")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Unauthorized to change settings")
    @ns.expect(settings_patch_req)
    def patch(self):
        """Update settings."""
        req = {
            k: v for k, v in settings_patch_req.parse_args().items() if v is not None
        }
        api.config.change_settings(req)
        return jsonify({"success": True})
