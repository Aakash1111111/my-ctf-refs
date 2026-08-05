#!/usr/bin/env python3

"""
./add-web-user.py -u username -p password -e email

Adds a user account to the website.
"""

import api

import argparse
import os
import sys

def main(args):
    # map arguments into parameter names expected by the API
    user = {}
    user["username"] = args.user
    user["password"] = args.password
    user["email"] = args.email
    user["firstname"] = args.first
    user["lastname"] = args.last
    user["country"] = args.country
    user["affiliation"] = args.affiliation
    user["usertype"] = args.type
    user["demo"] = {}

    exists = api.user.get_user(name=args.user)
    if exists is not None:
        # only warn to allow repeated adds of the same user in an automated context
        print("WARN: user already exists, not modified: {}".format(args.user), file=sys.stderr)
        print(exists["uid"])
        return

    try:
        uid = api.user.add_user(user)
        print(uid)
    except api.PicoException as e:
        print("ERROR: failed to add user", file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Add Web User")

    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("-e", "--email", required=True)

    parser.add_argument("-f", "--first", default="Auto")
    parser.add_argument("-l", "--last", default="User")
    parser.add_argument("-c", "--country", default= "US")
    parser.add_argument("-a", "--affiliation", default="")
    parser.add_argument("-t", "--type", default="")

    args = parser.parse_args()

    # set default picoCTF settings
    if 'APP_SETTINGS_FILE' not in os.environ:
        os.environ['APP_SETTINGS_FILE'] = '/picoCTF-web-config/deploy_settings.py'
    with api.create_app().app_context():
        main(args)
