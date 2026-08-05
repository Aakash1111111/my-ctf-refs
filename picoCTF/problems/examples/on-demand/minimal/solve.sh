#!/bin/bash

[ -z "$1" ] || [ -z "$2" ] && echo "usage: ./solve.sh HOST PORT" && exit 1

echo "hello" | nc $1 $2
