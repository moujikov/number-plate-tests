#!/usr/bin/env bash

./docker/ftp/build.sh
./docker/primeskud.web/build.sh
./docker/processor/build.sh
./docker/scheduler/build.sh
./docker/worker/build.sh
