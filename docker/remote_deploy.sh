#! /usr/bin/env bash

set -eu

if [[ $# != 1 ]]; then
    echo "USAGE: remote_deploy.sh host"

    exit 1
fi

HOST="$1"
LOCAL_BUILD_DIR=".deploy-build"
REMOTE_BUILD_DIR="~/snoring-bot-build"

echo ">>> Cleaning up local build directory ($LOCAL_BUILD_DIR)..."
rm -rf "$LOCAL_BUILD_DIR"
mkdir -p "$LOCAL_BUILD_DIR"

echo ">>> Building images..."
./build-irc.sh

echo ">>> Exporting images..."
docker save -o "$LOCAL_BUILD_DIR/images.tar" snoring-bot

# Remove the remote build directory
echo ">>> Cleaning up remote build directory on $1 ($REMOTE_BUILD_DIR)..."
ssh -t "deploy@$1" "rm -rf $REMOTE_BUILD_DIR"

echo ">>> Copying local build directory to remote host $1..."
cp run-irc.sh $LOCAL_BUILD_DIR/
scp -r -O $LOCAL_BUILD_DIR "deploy@$1:$REMOTE_BUILD_DIR"

echo ">>> Running deployment..."
ssh -t "deploy@$1" "(
    cd $REMOTE_BUILD_DIR
    docker load -i images.tar
    ./run-irc.sh
)"

echo ">>> Cleaning up..."
rm -rf "$LOCAL_BUILD_DIR"
