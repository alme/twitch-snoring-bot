# /usr/bin/env bash

set -eu

# Clean up containers
docker rm -f snoring-bot-irc

# Create network if it doesn't already exist
[[ $(docker network ls | grep snoring-bot-net; echo $?) == 1 ]] && docker network create snoring-bot-net

# Run containers
docker run -dt \
    --name snoring-bot-irc \
    --restart always \
    --network snoring-bot-net \
    --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 \
    -v snoring-bot-store:/store \
    snoring-bot-irc --playsounds "$@"
