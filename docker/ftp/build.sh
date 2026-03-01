#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-ftp \
                               -f ./docker/ftp/Dockerfile .
