#!/bin/bash

[ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] && echo "usage: ./solve.sh HOST KEY_PORT SSH_PORT" && exit 1

# get key from key delivery service
echo "" | nc $1 $2 > key
chmod 600 key

# connect to ssh with the key
ssh -o "StrictHostKeyChecking=no" \
    -o "UserKnownHostsFile /dev/null" \
    -o "LogLevel ERROR" \
    challenge@$1 -p $3 \
    -i key \
    "cat flag"

# clean up
rm key
