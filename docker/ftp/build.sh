#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-ftp \
                               -f ./docker/ftp/Dockerfile .

mkdir -p ./_data/ftp/camera-1
mkdir -p ./_data/ftp/camera-2
