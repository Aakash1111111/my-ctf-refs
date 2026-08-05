import grp
import json
import os
import pwd
import subprocess
import time
from os.path import join

# Workaround for https://github.com/picoCTF/picoCTF/issues/478
# (see https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/1869115)
import sys
sys.path += ["/usr/local/lib/python2.7/dist-packages", "/usr/lib/python2.7/dist-packages"]

import requests

DEFAULT_USER = "nobody"
LOCAL_ROOT = "/opt/hacksports/local/"
COMPETITORS_GROUP = "competitors"
USER_QUOTA_FILE = "/aquota.user"
USER_QUOTA = {
    "block_soft": "97M",
    "block_hard": "100M",
    "inode_soft": "2950",
    "inode_hard": "3000",
}

config_file = join(LOCAL_ROOT, "local_config.json")
config = json.loads(open(config_file).read())
SERVER = config["web_server"]
LIMIT_BYPASS = config["rate_limit_bypass_key"]
TIMEOUT = 5

pamh = None


def competition_active():
    r = requests.get(
        SERVER + "/api/v1/status", headers={"user-agent": "picoCTF Shell Server"}
    )
    return json.loads(r.text)["competition_active"]


def run_login(user, password):
    r = requests.post(
        SERVER + "/api/v1/user/login",
        headers={"user-agent": "picoCTF Shell Server", "Limit-Bypass": LIMIT_BYPASS},
        json={"username": user, "password": password},
        timeout=TIMEOUT,
    )
    if "success" in json.loads(r.text):
        return "Successfully logged in"
    else:
        return str(json.loads(r.text)["message"])


def display(string):
    message = pamh.Message(pamh.PAM_TEXT_INFO, string)
    pamh.conversation(message)


def prompt(string):
    message = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, string)
    return pamh.conversation(message)


def server_user_exists(user):
    if not competition_active():
        return False
    result = run_login(user, "`&/")
    return result == "Incorrect password"


def secure_user(user):
    home = pwd.getpwnam(user).pw_dir

    # Append only bash history
    subprocess.check_output(["touch", os.path.join(home, ".bash_history")])
    subprocess.check_output(
        ["chown", "root:" + user, os.path.join(home, ".bash_history")]
    )
    subprocess.check_output(["chmod", "660", os.path.join(home, ".bash_history")])
    subprocess.check_output(["chattr", "+a", os.path.join(home, ".bash_history")])

    # Secure bashrc
    subprocess.check_output(
        [
            "cp",
            "/opt/hacksports/shared/config/securebashrc",
            os.path.join(home, ".bashrc"),
        ]
    )
    subprocess.check_output(["chown", "root:" + user, os.path.join(home, ".bashrc")])
    subprocess.check_output(["chmod", "755", os.path.join(home, ".bashrc")])
    subprocess.check_output(["chattr", "+a", os.path.join(home, ".bashrc")])

    # Secure profile
    subprocess.check_output(["chown", "root:" + user, os.path.join(home, ".profile")])
    subprocess.check_output(["chmod", "755", os.path.join(home, ".profile")])
    subprocess.check_output(["chattr", "+a", os.path.join(home, ".profile")])

    # User should not own their home directory
    subprocess.check_output(["chown", "root:" + user, home])
    subprocess.check_output(["chmod", "1770", home])

    # Check if user quota is enabled, if so, add quota for this user
    if os.path.exists(USER_QUOTA_FILE):
        subprocess.check_output(
            [
                "/usr/sbin/setquota",
                user,
                USER_QUOTA["block_soft"],
                USER_QUOTA["block_hard"],
                USER_QUOTA["inode_soft"],
                USER_QUOTA["inode_hard"],
                "/",
            ]
        )


def pam_sm_authenticate(pam_handle, flags, argv):
    global pamh
    pamh = pam_handle

    try:
        user = pamh.get_user(None)
    except (pamh.exception, e):
        return e.pam_result

    try:
        entry = pwd.getpwnam(user)
        group = grp.getgrnam(COMPETITORS_GROUP)
        # local account exists and server account exists
        if server_user_exists(user) and user in group.gr_mem:
            response = prompt(
                "Enter your platform password (characters will be hidden): "
            )
            result = run_login(user, response.resp)

            if "Successfully logged in" in result:
                return pamh.PAM_SUCCESS
        else:
            return pamh.PAM_USER_UNKNOWN

    # local user account does not exist
    except KeyError as e:
        try:
            if server_user_exists(user):
                subprocess.check_output(
                    [
                        "/usr/sbin/useradd",
                        "-m",
                        "-G",
                        COMPETITORS_GROUP,
                        "-s",
                        "/bin/bash",
                        user,
                    ]
                )
                secure_user(user)

                display("Welcome {}!".format(user))
                display("Your shell server account has been created.")
                prompt("Please press enter and reconnect.")

                # this causes the connection to close
                return pamh.PAM_SUCCESS
            else:
                # sleep before displaying error message to slow down scanners
                time.sleep(3)
                display(
                    "Competition has not started or username does not exist on the platform website."
                )
                return pamh.PAM_USER_UNKNOWN

        except Exception as e:
            pass

    # sleep before failing to slow down scanners
    time.sleep(3)
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS
