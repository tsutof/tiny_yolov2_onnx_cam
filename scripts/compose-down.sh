#!/usr/bin/env bash

set -eu

source scripts/docker_base.sh

export BASE_IMAGE=${BASE_IMAGE}
export L4T_VERSION=${L4T_VERSION}

sudo -E ~/.local/bin/docker-compose down
