#!/usr/bin/env python3

"""
./gen_vault.py

Utility script to generate a secure ansible-vault file for use in deploying a
production platform.

This script is not intended to replace the ansible-vault command. It simply
exists to streamline a secure default setup (e.g. no user decisions required).
As such it intentionally takes no arguments and provides no configuration
options
"""

import getpass
import os
import random
import string
import subprocess

# Contents of the vault. All sensitive variables should be reflected here.
VAULT_TEMPLATE = """
# web
vault_web_admin_pw                    : "{web_pw}"

# web API
vault_flask_app_secret_key            : "{flask_secret}"
vault_flask_app_rate_limit_bypass_key : "{bypass_key}"

# shell
vault_shell_manager_deploy_secret     : "{deploy_secret}"

# db
vault_picoAdmin_db_password           : "{admin_pw}"
vault_picoWeb_db_password             : "{db_pw}"
vault_redis_db_password               : "{redis_pw}"
"""

# keys must match the above template
VAULT_KEYS = ["web_pw", "flask_secret", "bypass_key", "deploy_secret",
        "admin_pw", "redis_pw", "db_pw"]

VAULT_PATH = "vault.yml"
VAULT_PASS_PATH = "vault_pass.txt"
VAULT_WARN_MSG = """WARNING: vault file exists.

Currently the picoCTF automation does not support changing all secrets in an
automated fashion.

If you have an existing platform deployed and want to roll your credentials it
is recommend that you do so manually and then update the vault.yml with:

    ansible-vault edit vault.yml

If you have not yet deployed the platform just remove the vault.yml file and
re-run this command."""


def gen_random_string(n=24):
    """Returns a random n-length string, suitable for a password or random secret"""
    # RFC 3986 section 2.3. unreserved characters (no special escapes required)
    char_set = string.ascii_letters +  string.digits + "-._~"
    return "".join(random.choices(char_set, k=n))

def gen_random_config():
    """Generates random values for all keys in the config"""
    config = {}
    for k in VAULT_KEYS:
        config[k] = gen_random_string()
    return VAULT_TEMPLATE.format(**config)

def write_file(fname, string):
    with open(fname, 'wb') as out:
        out.write(string.encode('utf-8'))

def vault_encrypt():
    cmd = ["ansible-vault", "encrypt", VAULT_PATH]
    res = subprocess.run(cmd, check=True)

def file_exists(fname):
    return os.path.isfile(fname)

def get_vault_pass():
    return getpass.getpass("Enter a password for your vault: ") + "\n"

def main():
    if not file_exists(VAULT_PASS_PATH):
        write_file(VAULT_PASS_PATH, get_vault_pass())
    if not file_exists(VAULT_PATH):
        write_file(VAULT_PATH, gen_random_config())
        vault_encrypt()
    else:
        print(VAULT_WARN_MSG)

if __name__ == '__main__':
    main()
