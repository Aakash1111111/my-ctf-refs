"""Module dealing with shell server integration."""
import json

import spur

import api
from api import PicoException


def get_server(sid):
    """
    Return the server dict corresponding to the sid provided.

    Args:
        sid: the server id to lookup

    Returns:
        The server dict, or None if the server was not found

    """
    db = api.db.get_conn()
    return db.shell_servers.find_one({"sid": sid}, {"_id": 0})


def get_connection(sid):
    """
    Connect to a shell server via SSH.

    Args:
        sid: the shell server ID

    Returns:
        spur SshShell connection object

    Raises:
        PicoException if cannot connect to the host, authenticate, or
        run shell_manager successfully

    """
    server = get_server(sid)

    try:
        shell = None
        # default to keypath if provided
        if server["keypath"] != "":
            shell = spur.SshShell(
                hostname=server["host"],
                username=server["username"],
                private_key_file=server["keypath"],
                port=server["port"],
                missing_host_key=spur.ssh.MissingHostKey.accept,
                connect_timeout=2,
            )
        else:
            shell = spur.SshShell(
                hostname=server["host"],
                username=server["username"],
                password=server["password"],
                port=server["port"],
                missing_host_key=spur.ssh.MissingHostKey.accept,
                connect_timeout=2,
            )
        shell.run(["echo", "connected"])
    except spur.ssh.ConnectionError as e :
        raise PicoException(
            "Cannot connect to {}@{}:{}\n{}".format(
                server["username"], server["host"], server["port"], e
            )
        )
    return shell


def add_server(*ignore, name, host, port, username, password="", protocol, server_number, keypath=""):
    """
    Add a shell server to the pool of servers.

    Servers are automatically assigned a server_number based on the current
    number of servers if not explicitly specified.

    Kwargs:
        name: display name
        host: hostname
        port: SSH port
        username
        password
        protocol: HTTP or HTTPS
        server_number
    Returns:
       sid of the newly created shell server
    Raises:
        PicoException: a shell server with this server_number already exists
    """
    db = api.db.get_conn()

    if not server_number:
        server_number = db.shell_servers.count() + 1

    if db.shell_servers.find_one({"server_number": server_number}) is not None:
        raise PicoException(
            "Shell server with this server_number " + "already exists.", status_code=409
        )

    sid = api.common.token()
    db.shell_servers.insert_one(
        {
            "sid": sid,
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "keypath": keypath,
            "protocol": protocol,
            "server_number": server_number,
        }
    )
    return sid


def update_server(sid, updates):
    """
    Update a shell server.

    Args:
        sid: the sid of the server to update
        updates: dict of updated shell server fields

    Returns:
        sid of the updated server (unchanged), or
        None if the provided sid was not found

    Raises:
        PicoException if attempting to set server_number to one already
        in use by a different server

    """
    db = api.db.get_conn()

    # Make sure we are not duplicating a server number
    if "server_number" in updates and db.shell_servers.find_one(
        {"server_number": updates["server_number"], "sid": {"$ne": sid}}
    ):
        raise PicoException(
            "Another shell server with this server_number " + "already exists.",
            status_code=409,
        )

    success = db.shell_servers.find_one_and_update({"sid": sid}, {"$set": updates})
    if not success:
        return None
    else:
        return sid


def remove_server(sid):
    """
    Remove a shell server from the pool of servers.

    Args:
        sid: the sid of the server to be removed

    Returns:
        sid of the removed shell server, or
        None if the provided sid was not found

    """
    db = api.db.get_conn()
    res = db.shell_servers.find_one_and_delete({"sid": sid})
    if res is None:
        return None
    else:
        return sid


def get_all_servers():
    """Return the full list of shell servers."""
    db = api.db.get_conn()
    return list(db.shell_servers.find({}, {"_id": 0}))


def get_assigned_server():
    """Return the assigned shell server for the currently logged-in team."""
    db = api.db.get_conn()

    settings = api.config.get_settings()
    match = {}
    if settings["shell_servers"]["enable_sharding"]:
        team = api.team.get_team()
        match = {"server_number": team.get("server_number", 1)}

    servers = list(db.shell_servers.find(match, {"_id": 0}))

    if len(servers) == 0 and settings["shell_servers"]["enable_sharding"]:
        raise PicoException(
            "Your assigned shell server is currently down." + "Please contact an admin."
        )

    return servers


def get_problem_status_from_server(sid):
    """
    Connect to the server and check the status of the problems running there.

    Runs `sudo shell_manager status --json` and parses its output.

    Closes connection after running command.

    Args:
        sid: The sid of the server to check

    Returns:
        A tuple containing:
            - True if all problems are online and false otherwise
            - The output data of shell_manager status --json

    """
    shell = get_connection(sid)

    with shell:
        output = shell.run(
            ["sudo", "/picoCTF-env/bin/shell_manager", "status", "--json"],
            encoding="utf-8",
        ).output
    data = json.loads(output)

    all_online = True

    for problem in data["problems"]:
        for instance in problem["instances"]:
            # if the service is not working
            if not instance["service"]:
                all_online = False

            # if the connection is not working and it is a remote challenge
            if not instance["connection"] and instance["port"] is not None:
                all_online = False

    return (all_online, data)


def get_publish_output(sid):
    """
    Connect to the server and capture the `shell_manager publish` output.

    Args:
        sid: the shell server ID to run the command on

    Returns:
        the output as a dict

    """
    shell = get_connection(sid)

    with shell:
        status = shell.run(
            ["sudo", "/picoCTF-env/bin/shell_manager", "status"],
            allow_error=True,
            encoding="utf-8",
        )
        if status.return_code != 0:
            raise PicoException(
                "Not all instances online, check shell_manager.",
                data={"stderr": status.stderr_output},
            )
        result = shell.run(
            ["sudo", "/picoCTF-env/bin/shell_manager", "publish"], encoding="utf-8"
        )
    return json.loads(result.output)


def get_assigned_server_number(new_team=True, tid=None):
    """
    Assign a server number based on current team count and configured stepping.

    Returns:
         (int) server_number

    """
    settings = api.config.get_settings()["shell_servers"]
    db = api.db.get_conn()

    if new_team:
        team_count = db.teams.count()
    else:
        if not tid:
            raise PicoException("tid must be specified.")
        oid = db.teams.find_one({"tid": tid}, {"_id": 1})
        if not oid:
            raise PicoException("Invalid tid.")
        team_count = db.teams.count({"_id": {"$lt": oid["_id"]}})

    assigned_number = 1

    steps = settings["steps"]

    if steps:
        if team_count < steps[-1]:
            for i, step in enumerate(steps):
                if team_count < step:
                    assigned_number = i + 1
                    break
        else:
            assigned_number = (
                1
                + len(steps)
                + (team_count - steps[-1]) // settings["default_stepping"]
            )

    else:
        assigned_number = team_count // settings["default_stepping"] + 1

    if settings["limit_added_range"]:
        max_number = list(
            db.shell_servers.find({}, {"server_number": 1})
            .sort("server_number", -1)
            .limit(1)
        )[0]["server_number"]
        return min(max_number, assigned_number)
    else:
        return assigned_number


def reassign_teams(include_assigned=False):
    """Reassign teams to shell servers."""
    db = api.db.get_conn()

    if include_assigned:
        teams = api.team.get_all_teams()
    else:
        teams = list(
            db.teams.find({"server_number": {"$exists": False}}, {"_id": 0, "tid": 1})
        )

    for team in teams:
        old_server_number = team.get("server_number")
        server_number = get_assigned_server_number(new_team=False, tid=team["tid"])
        if old_server_number != server_number:
            db.teams.update(
                {"tid": team["tid"]},
                {"$set": {"server_number": server_number, "instances": {}}},
            )
            # Re-assign instances
            api.problem.get_unlocked_pids(team["tid"])

    return len(teams)
