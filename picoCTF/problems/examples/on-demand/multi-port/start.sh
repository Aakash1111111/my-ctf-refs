#!/bin/bash

set -e

# start ssh service
service ssh start

# start the key delivery service
socat -U TCP4-LISTEN:5555,reuseaddr,fork OPEN:/opt/challenge
