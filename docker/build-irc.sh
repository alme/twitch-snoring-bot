#! /usr/bin/env bash

BUILD_DIR="./.irc-build"

mkdir -p "${BUILD_DIR}"

eval $(ansible-vault view --vault-password-file vault.password vars/irc.vault)

# Write config files
envsubst < templates/config.py > "${BUILD_DIR}/config.py"

# Build images
docker build -f base/python-irc.base.Dockerfile --tag snoring-bot ..

# Clean up
rm -rf "${BUILD_DIR}"