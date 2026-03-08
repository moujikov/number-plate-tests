#!/usr/bin/env bash

set -eu -o pipefail

docker run --rm -t --name number-plates-database \
  --env-file ./docker/database/.env \
  --volume ./docker/database/init.sql:/docker-entrypoint-initdb.d/init.sql \
  --volume number-plates_database:/var/lib/postgresql \
  --publish 5432:5432 \
  postgres:18-alpine
