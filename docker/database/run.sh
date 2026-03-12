#!/usr/bin/env bash

set -eu -o pipefail

docker run --rm -t --name number-plates-database \
  --env-file ./docker/database/.env \
  --volume ./docker/database/init:/docker-entrypoint-initdb.d \
  --volume number-plates_database:/var/lib/postgresql \
  --mount type=bind,src="./docker/.secrets/db_password_postgres",dst=/run/secrets/db_password_postgres,readonly \
  --mount type=bind,src="./docker/.secrets/db_password_processor",dst=/run/secrets/db_password_processor,readonly \
  --mount type=bind,src="./docker/.secrets/db_password_skud",dst=/run/secrets/db_password_skud,readonly \
  --mount type=bind,src="./docker/.secrets/db_password_frontend",dst=/run/secrets/db_password_frontend,readonly \
  --publish 5432:5432 \
  postgres:18-alpine
