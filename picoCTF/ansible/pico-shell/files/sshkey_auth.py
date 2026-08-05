#!/usr/bin/env python3

import json
import pwd
import sys
from os import path

import requests

LOCAL_ROOT = "/opt/hacksports/local/"

config_file = path.join(LOCAL_ROOT, "local_config.json")
config = json.loads(open(config_file).read())
SERVER = config["web_server"]
LIMIT_BYPASS = config["rate_limit_bypass_key"]
TIMEOUT = 5
SYSTEM_USERS = ["vagrant", "ubuntu"]


def competition_active():
    r = requests.get(
        SERVER + "/api/v1/status", headers={"user-agent": "picoCTF Shell Server"}
    )
    return json.loads(r.text)["competition_active"]


def try_login(user):
    r = requests.post(
        SERVER + "/api/v1/user/login",
        headers={"user-agent": "picoCTF Shell Server", "Limit-Bypass": LIMIT_BYPASS},
        json={"username": user, "password": "-"},
        timeout=TIMEOUT,
    )
    return str(json.loads(r.text)["message"])


def server_valid_user(user):
    if user in SYSTEM_USERS:
        return True
    if not competition_active():
        return False
    result = try_login(user)
    return result == "Incorrect password"


def main(user):
    if not server_valid_user(user):
        exit(0)
    else:
        auth_keys_dir = path.join(pwd.getpwnam(user).pw_dir, ".ssh")
        auth_keys_file = path.join(auth_keys_dir, "authorized_keys")
        if path.exists(auth_keys_file):
            with open(auth_keys_file, "r") as fin:
                print(fin.read())
        else:
            exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("No user specified")
        sys.exit("Bad args")
    else:
        main(sys.argv[1])
