#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t moujikov/number-plates-primeskud.web \
                               -f ./docker/primeskud.web/Dockerfile .
