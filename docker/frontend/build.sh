#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-frontend \
                               -f ./docker/frontend/Dockerfile .
