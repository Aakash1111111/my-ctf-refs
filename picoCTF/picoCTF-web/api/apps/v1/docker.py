"""
Docker related endpoints.

XXX.
"""

from flask import jsonify
from flask_restplus import Namespace, Resource

import api
from api import docker
from api import block_before_competition, PicoException, require_admin, require_login

import string

ns = Namespace("docker", description="On-Demand (docker) instance management")

@block_before_competition
@require_login
@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Instance not found")
@ns.route("/")
class Docker(Resource):
    """
    Manage all running DockerContainer instances
    """

    def delete(self):
        """
        Fresh container environment. Kill any running DockerContainer.
        """

        # Containers are mapped to teams
        user_account = api.user.get_user()
        tid = user_account['tid']

        # Ensure we know ground truth for running containers
        live = api.docker.ensure_consistency(tid)

        res = []
        # Kill any live containers
        for container in live:
            res.append(api.docker.delete(container.id))

        if all(res):
            return jsonify({"success": True, "message": "All on demand challenges reset."})
        else:
            return jsonify({"success": False, "message": "Error resetting on demand challenges"})

@block_before_competition
@require_login
@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Instance not found")
@ns.route("/<string:digest>")
class DockerImage(Resource):
    """
    The underlying docker images associated with a problem instance. Used to
    lauch a running DockerContainer.
    """

    def post(self, digest):
        """
        Create a running instance from the container image digest
        """
        # Containers are mapped to teams
        user_account = api.user.get_user()
        tid = user_account['tid']

        # fail fast on invalid requests
        if any(char not in string.hexdigits + "sha:" for char in digest):
            raise PicoException("Invalid image digest", 400)

        # Create the container
        result = api.docker.create(tid, digest)

        return jsonify({"success": result['success'], "message": result['message']})


@block_before_competition
@require_login
@ns.response(200, "Success")
@ns.response(401, "Not logged in")
@ns.response(403, "Not authorized")
@ns.response(404, "Instance not found")
@ns.route("/<string:digest>/<string:container_id>")
class DockerContainer(Resource):
    """
    A running instance created from a DockerImage.
    """

    def delete(self, digest, container_id):
        """
        Stop a running container.
        """

        # fail fast on invalid requests
        if any(char not in string.hexdigits for char in container_id):
            raise PicoException("Invalid container ID", 400)

        # Delete the container
        result = api.docker.delete(container_id)

        if result:
            return jsonify({"success": True, "message": "Challenge stopped"})
        else:
            return jsonify({"success": False, "message": "Error stopping challenge"})

    def put(self, digest, container_id):
        """
        Reset (delete and start) a running DockerContainer instance
        """

        # Containers are mapped to teams
        user_account = api.user.get_user()
        tid = user_account['tid']


        # fail fast on invalid requests
        if any(char not in string.hexdigits for char in container_id):
            raise PicoException("Invalid container ID", 400)
        if any(char not in string.hexdigits + "sha:" for char in digest):
            raise PicoException("Invalid image digest", 400)

        # Delete the container
        del_result = api.docker.delete(container_id)

        # Create the container
        create_result = api.docker.create(tid, digest)

        if del_result and create_result["success"]:
            return jsonify({"success": True,
                "message": "Challenge reset.\nBe sure to use the new port."})
        else:
            return jsonify({"success": False, "message": "Error resetting challenge"})
