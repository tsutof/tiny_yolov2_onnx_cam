#!/usr/bin/env bash

DOCKER_COMPOSE_PATH=`which docker-compose`

set -eu

source scripts/docker_base.sh

cp /etc/apt/sources.list.d/nvidia-l4t-apt-source.list .
cp /etc/apt/trusted.gpg.d/jetson-ota-public.asc .

export BASE_IMAGE=${BASE_IMAGE}
export L4T_VERSION=${L4T_VERSION}

if [ -z "${DOCKER_COMPOSE_PATH}" ]; then
    DOCKER_COMPOSE_PATH="${HOME}/.local/bin/docker-compose"
fi

sudo -E ${DOCKER_COMPOSE_PATH} up
