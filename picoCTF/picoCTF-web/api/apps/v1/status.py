"""Endpoint for platform status."""
import datetime

from flask import jsonify
from flask_restplus import Namespace, Resource

import api

ns = Namespace("status", description="Information about the platform status")


@ns.route("")
class Status(Resource):
    """Get information about the platform status."""

    def get(self):
        """
        Get information about the platform status.

        The main purpose is to have an endpoint to check if the platform is up,
        but also reports some settings for convenience.

        Previous versions of this endpoint included user/team status if
        a user was logged in - that information should now be retreived
        from their respective endpoints.
        """
        settings = api.config.get_settings()
        return jsonify(
            {
                "competition_active": api.config.check_competition_active(),
                "time": int(datetime.datetime.utcnow().timestamp()),
            }
        )
