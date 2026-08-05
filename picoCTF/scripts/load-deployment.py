#!/usr/bin/env python3

"""
./load-deployment.py

Loads a deployment from a previously configured shell server.
"""

import api

import argparse
import os
import sys


def main(args):
    server = None

    all_servers = api.shell_servers.get_all_servers()
    for s in all_servers:
        if s["name"] == args.name:
            server = s
            break

    if server is None:
        print("ERROR: shell server not found: {}".format(args.name), file=sys.stderr)
        sys.exit(1)

    sid = server["sid"]
    try:
        # Load problems and bundles from the shell server
        output = api.shell_servers.get_publish_output(sid)
        output["sid"] = sid
        api.problem.load_published(output)
        print("Deployment loaded")

        # Enable problems
        if args.enable:
            for p in api.problem.get_all_problems(show_disabled=True):
                api.problem.set_problem_availability(p["pid"], disabled=False)
            print("Problems enabled")

        # Enable locking on bundles
        if args.lock:
            for b in api.bundles.get_all_bundles():
                bid = api.bundles.set_bundle_dependencies_enabled(b["bid"], enabled=True)
                if bid is None:
                    print("ERROR: locking bundle", file=sys.stderr)
                    sys.exit(1)

            print("Bundles locking")

    except Exception as e:
        print("ERROR: failed to load problems", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Load Deployment from Shell")
    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-e", "--enable", action="store_true")
    parser.add_argument("-l", "--lock", action="store_true")
    args = parser.parse_args()

    # set default picoCTF settings
    if 'APP_SETTINGS_FILE' not in os.environ:
        os.environ['APP_SETTINGS_FILE'] = '/picoCTF-web-config/deploy_settings.py'
    with api.create_app().app_context():
        main(args)
