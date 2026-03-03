#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-processor \
                               -f ./docker/processor/Dockerfile .
