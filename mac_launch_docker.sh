#!/usr/bin/env bash
# This file launches spinmob in a display-ready docker container

# Credit to: http://stackoverflow.com/a/36190462/2689923

# Requires Xquartz and socat installed!

# Define what we are running here.
CONTAINER=spinmob
COMMAND=/bin/bash
NIC=en0

# Grab the ip address of this box
IPADDR=$(ifconfig $NIC | grep "inet " | awk '{print $2}')

DISP_NUM=$(jot -r 1 100 200)  # random display number between 100 and 200

PORT_NUM=$((6000 + DISP_NUM)) # so multiple instances of the container won't interfer with eachother

# Set up a socket for the display
socat TCP-LISTEN:${PORT_NUM},reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" 2>&1 > /dev/null &

XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth.$USER.$$
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

# Actually run the spinmob container
# This sets the port access to 8888
# The file storage (e.g., accessible from jupyter) to Documents/notebooks
# This also sets up the display (for e.g., popouts if they happen (?))
docker run \
    -it \
    --workdir="/workspace" \
    -p 8888:8888 \
    -v "/Users/$USER/Documents/notebooks:/workspace" \
    -v $XSOCK:$XSOCK:rw \
    -v $XAUTH:$XAUTH:rw \
    -e DISPLAY=$IPADDR:$DISP_NUM \
    -e XAUTHORITY=$XAUTH \
    $CONTAINER \
    $COMMAND

rm -f $XAUTH
kill %1       # Kill the socat job launched above
