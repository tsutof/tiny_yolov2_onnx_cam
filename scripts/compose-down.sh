#!/usr/bin/env bash

set -eu

source scripts/docker_base.sh

export BASE_IMAGE=${BASE_IMAGE}

sudo -E ~/.local/bin/docker-compose down
