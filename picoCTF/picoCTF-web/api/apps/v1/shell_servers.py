"""Shell server related endpoints."""
from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import PicoException, require_admin, require_login

from .schemas import (
    shell_server_reassignment_req,
    shell_server_patch_req,
    shell_server_req,
    shell_server_list_req,
)

ns = Namespace("shell_servers", description="Shell server management")


@ns.route("")
class ShellServerList(Resource):
    """Get the list of shell servers, or add a new server."""

    @require_login
    @ns.response(200, "Success")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Unauthorized")
    @ns.expect(shell_server_list_req)
    def get(self):
        """
        Get the list of shell servers.

        By default, returns only your assigned shell servers.
        Admins can override this by specifying '?assigned_only=false'.
        """
        req = shell_server_list_req.parse_args(strict=True)
        if req["assigned_only"] is False:
            if api.user.get_user().get("admin", False):
                return api.shell_servers.get_all_servers(), 200
            else:
                raise PicoException(
                    "You must be an admin to use ?assigned_only=false.", status_code=403
                )
        else:
            # Get assigned shell servers
            return jsonify(
                [
                    {"host": server["host"], "protocol": server["protocol"]}
                    for server in api.shell_servers.get_assigned_server()
                ]
            )

    @require_admin
    @ns.expect(shell_server_req)
    @ns.response(201, "Shell server added")
    @ns.response(400, "Error parsing request")
    @ns.response(401, "Not logged in")
    @ns.response(403, "Not authorized")
    @ns.response(409, "server_number conflicts with existing server")
    def post(self):
        """Add a new shell server."""
        req = shell_server_req.parse_args(strict=True)
        sid = api.shell_servers.add_server(**req)
        res = jsonify({"success": True, "sid": sid})
        res.status_code = 201
        return res


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Shell server not found")
@ns.route("/<string:server_id>")
class ShellServer(Resource):
    """Get, update, or delete a specific shell server."""

    @require_admin
    def get(self, server_id):
        """Retrieve a specific shell server."""
        res = api.shell_servers.get_server(server_id)
        if not res:
            raise PicoException("Shell server not found", status_code=404)
        else:
            return res, 200

    @require_admin
    @ns.expect(shell_server_req)
    @ns.response(400, "Error parsing request")
    @ns.response(409, "server_number conflicts with existing server")
    def put(self, server_id):
        """Replace a specific shell server."""
        req = shell_server_req.parse_args(strict=True)
        sid = api.shell_servers.update_server(server_id, req)
        if sid is None:
            raise PicoException("Shell server not found", status_code=404)
        return jsonify({"success": True, "sid": sid})

    @require_admin
    @ns.expect(shell_server_patch_req)
    @ns.response(400, "Error parsing request")
    @ns.response(409, "server_number conflicts with existing server")
    def patch(self, server_id):
        """Update an existing shell server."""
        req = {
            k: v
            for k, v in shell_server_patch_req.parse_args().items()
            if v is not None
        }
        sid = api.shell_servers.update_server(server_id, req)
        if sid is None:
            raise PicoException("Shell server not found", status_code=404)
        return jsonify({"success": True, "sid": sid})

    @require_admin
    def delete(self, server_id):
        """Delete a specific shell server."""
        sid = api.shell_servers.remove_server(server_id)
        if sid is None:
            raise PicoException("Shell server not found", status_code=404)
        return jsonify({"success": True})


@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Shell server not found")
@ns.route("/<string:server_id>/status")
class ShellServerStatus(Resource):
    """Get the problem status for a specific shell server."""

    @require_admin
    def get(self, server_id):
        """Get the problem status on a specific shell server."""
        all_online, data = api.shell_servers.get_problem_status_from_server(server_id)
        return jsonify({"all_problems_online": all_online, "status": data})


@ns.route("/update_assignments")
@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(500, "Sharding not enabled")
class ShellServerAssignment(Resource):
    """Update team to shell server mappings when sharding is enabled."""

    @require_admin
    @ns.expect(shell_server_reassignment_req)
    def post(self):
        """Update teams' shell server assignments."""
        if not api.config.get_settings()["shell_servers"]["enable_sharding"]:
            raise PicoException(
                "Sharding must be enabled to update server assignments.", 500
            )
        req = shell_server_reassignment_req.parse_args(strict=True)
        include_assigned = req["include_assigned"] is True
        assigned_count = api.shell_servers.reassign_teams(
            include_assigned=include_assigned
        )
        return jsonify({"success": True, "teams_reassigned": assigned_count})
