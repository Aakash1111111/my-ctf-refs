#!/usr/bin/env python3

"""
./add-shell-server.py

Adds a shell server to the website.
"""
import api

import argparse
import os
import sys


def main(args):
    # If a server by this name exists short circuit no action necessary
    servers = api.shell_servers.get_all_servers()
    for s in servers:
        if s["name"] == args.name:
            print("WARN: shell server already exists, not modified: {}".format(args.name), file=sys.stderr)
            print(s["sid"], end="")
            return
    # server does not exist try to add
    try:
        sid = api.shell_servers.add_server(
            name=args.name,
            host=args.host,
            port=args.port,
            username=args.user,
            keypath=args.keypath,
            protocol=args.proto,
            server_number=args.server,
        )
        print(sid, end="")
    except Exception as e:
        print(e, file=sys.stderr)
        print("ERROR: failed to load shell server", file=sys.stderr)
        exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Add Shell Server")

    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-k", "--keypath", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--proto", required=True)
    parser.add_argument("--port", default="22")
    parser.add_argument("--server", default="1")

    args = parser.parse_args()

    # set default picoCTF settings
    if 'APP_SETTINGS_FILE' not in os.environ:
        os.environ['APP_SETTINGS_FILE'] = '/picoCTF-web-config/deploy_settings.py'
    with api.create_app().app_context():
        main(args)
