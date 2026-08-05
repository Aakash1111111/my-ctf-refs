#!/usr/bin/env python3

"""
./init-ctf.py

Initializes CTF settings. Only updates if the current scoreboard is missing or
if the start and end time are the same (default state).
"""

import api

import argparse
import os
import sys
from datetime import datetime, timedelta

def scoreboard_exists(name):
    for s in api.scoreboards.get_all_scoreboards():
        if s["name"] == name:
            return True
    return False

def main(args):

    # Add scoreboard only if it does not exist
    # XXX: 99 is a "magic" constant expected by scoreboard.jsx?
    if not scoreboard_exists(args.name):
        api.scoreboards.add_scoreboard(
                args.name,
                eligibility_conditions={},
                priority=99)
        print("Added scoreboard: {}".format(args.name))
    else:
        print("Scoreboard exists: {}".format(args.name))


    # only update if default (uninitialized state) to prevent clobbering any
    # user modified settings
    settings = api.config.get_settings()
    if settings["start_time"] == settings["end_time"] and args.start:
        now = datetime.now() 
        settings["start_time"] = now
        settings["end_time"] = now + timedelta(weeks=52)
        api.config.change_settings(settings)
        print("Started CTF")
    else:
        print("Event already has a start/end: {} - {}".format(
            settings["start_time"],
            settings["end_time"]))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Init CTF Settings")
    parser.add_argument("-g", "--global-scoreboard-name", required=True, dest="name")
    parser.add_argument("-s", "--start", action="store_true")
    args = parser.parse_args()

    # set default picoCTF settings
    if 'APP_SETTINGS_FILE' not in os.environ:
        os.environ['APP_SETTINGS_FILE'] = '/picoCTF-web-config/deploy_settings.py'
    with api.create_app().app_context():
        main(args)
