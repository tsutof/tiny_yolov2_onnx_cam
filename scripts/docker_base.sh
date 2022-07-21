#!/usr/bin/env bash

source scripts/l4t_version.sh

BASE_IMAGE="nvcr.io/nvidia/l4t-base:r$L4T_VERSION"
BASE_DEVEL="nvcr.io/nvidia/l4t-base:r$L4T_VERSION"


if [ $L4T_RELEASE -eq 32 ]; then
	if [ $L4T_REVISION_MAJOR -eq 5 ]; then
		if [ $L4T_REVISION_MINOR -eq 1 ]; then
			BASE_IMAGE="nvcr.io/nvidia/l4t-base:r32.5.0"
		elif [ $L4T_REVISION_MINOR -eq 2 ]; then
			BASE_IMAGE="nvcr.io/nvidia/l4t-base:r32.5.0"
		fi
    elif [ $L4T_REVISION_MAJOR -eq 7 ]; then
        if [ $L4T_REVISION_MINOR -eq 2 ]; then
            BASE_IMAGE="nvcr.io/nvidia/l4t-base:r32.7.1"
        fi
	fi
fi
	
echo "l4t-base image:  $BASE_IMAGE"