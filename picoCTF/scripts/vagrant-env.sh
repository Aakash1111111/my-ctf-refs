#!/bin/bash

# This script adds the custom WIP/SIP environment variables to the provided
# vagrant machines so that they are accessible during provisioning.

# Install to the profile of the ansible_user
INFILE=/home/vagrant/.profile

# Using sed technique to replace/append a line in file, ref:
# https://superuser.com/a/976712
sed -i "/^export SIP=/{h;s/=.*/=${SIP}/};\${x;/^$/{s//export SIP=${SIP}/;H};x}" ${INFILE}
sed -i "/^export WIP=/{h;s/=.*/=${WIP}/};\${x;/^$/{s//export WIP=${WIP}/;H};x}" ${INFILE}
