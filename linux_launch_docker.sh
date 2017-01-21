#!/usr/bin/env bash
# This file launches spinmob in a display-ready docker container

# Credit to: http://stackoverflow.com/a/36190462/2689923

# Define what we are running here.
CONTAINER=spinmob
COMMAND=/bin/bash

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
    -v "$HOME/Documents/notebooks:/workspace" \
    -v $XSOCK:$XSOCK \
    -v $XAUTH:$XAUTH \
    -e XAUTHORITY=$XAUTH \
    $CONTAINER \
    $COMMAND

rm -f $XAUTH
