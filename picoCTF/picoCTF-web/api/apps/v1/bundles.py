"""
Bundle related endpoints.

Bundle resources are treated differently as the source of truth for most of
their properties is the shell server(s). See ./problems.py for more info.
"""
from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import PicoException, require_admin

from .schemas import bundle_patch_req

ns = Namespace("bundles", description="Bundle management")


@ns.route("")
class BundleList(Resource):
    """Get the full list of bundles."""

    @require_admin
    @ns.response(200, "Success")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    def get(self):
        """Get the full list of bundles."""
        return jsonify(api.bundles.get_all_bundles())

    @ns.response(501, "Use the /problems endpoint")
    def patch(self):
        """Not implemented: use the /problems endpoint to update bundles."""
        raise PicoException(
            "Use the /problems endpoint to update bundles.", status_code=501
        )


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Bundle not found")
@ns.route("/<string:bundle_id>")
class Bundle(Resource):
    """Get or update the dependencies_enabled property of a specific bundle."""

    @require_admin
    def get(self, bundle_id):
        """Retrieve a specific bundle."""
        bundle = api.bundles.get_bundle(bundle_id)
        if not bundle:
            raise PicoException("Bundle not found", status_code=404)
        return jsonify(bundle)

    @require_admin
    @ns.response(400, "Error parsing request")
    @ns.expect(bundle_patch_req)
    def patch(self, bundle_id):
        """
        Update a specific bundle.

        The only valid field for this method is "dependencies_enabled".
        Other fields are pulled from the shell server, and
        can be updated via the /problems endpoint.
        """
        req = bundle_patch_req.parse_args(strict=True)
        bid = api.bundles.set_bundle_dependencies_enabled(
            bundle_id, req["dependencies_enabled"]
        )
        if not bid:
            raise PicoException("Bundle not found", status_code=404)
        else:
            return jsonify({"success": True})
