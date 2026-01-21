#!/bin/bash

DOCKER_BUILDKIT=1 docker build -t number-plate-tests -f ./Dockerfile .
