#!/usr/bin/env python3

"""
container_prune.py

Script to check containers launched by the picoCTF platform and delete those
which have passed their time-to-live.

The default TTL is 30 minutes or can be set with the CONTAINER_TTL environment
variable (seconds).

This script intentionally has limited dependencies (e.g. just the python standard
library) so that it can be deployed on any docker host as a cron job.
"""

import os
import subprocess
import time

def find_stale_containers(ttl):
    cmd = ['docker', 'ps', '-f', 'label=problem', '--format', '{{.ID}} {{.Label "created_at"}}']
    containers = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    stale = []
    for container_info in containers.stdout.decode().splitlines():
        parts = container_info.split()
        if len(parts) < 2:
            continue
        container_id, created_at = parts
        now = time.time()
        expire = int(created_at) + ttl
        t = expire - now
        if expire <= now:
            print(container_id, ": DELETE: expired %d s" % t)
            stale.append(container_id)
        else:
            print(container_id, ": live for : %d s" % t)
    return stale

def delete(stale):
    cmd = ['docker', 'kill'] + stale
    print("cleaning with: `{}`".format(" ".join(cmd)))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    if res.returncode == 0:
        print("\n------\nSuccess\n------")
    else:
        print("~~~ WARNING ~~")
        print(res.returncode)
        for line in res.stdout.decode().splitlines():
            print(line)


if __name__ == '__main__':
    print("\n------\n" + time.strftime("%Y-%m-%d %H:%M"))
    ttl = int(os.getenv('CONTAINER_TTL', 30*60)) # default to 30 minutes
    stale = find_stale_containers(ttl)
    if len(stale) > 0:
        delete(stale)
