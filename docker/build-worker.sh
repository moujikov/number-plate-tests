#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-worker \
                               -f ./docker/worker/Dockerfile .
