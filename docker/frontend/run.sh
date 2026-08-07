#!/usr/bin/env bash

set -eu -o pipefail

PORT=8000

usage() {
  cat <<EOF
Usage: ./docker/frontend/run.sh [--port <port>]

Options:
  --port, -p            Port to run the server on (default: ${PORT})
  --help, -h            Show this help

Examples:
  ./docker/frontend/run.sh
  ./docker/frontend/run.sh --port 8080
EOF
}

DOCKER_ENV_PARAMS=( -e "PYTHONDEVMODE=1" -e "LOG_LEVEL=DEBUG" )
url_id=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port|-p)
      PORT="${2:-}"
      shift 2
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;%
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

DOCKER_ENV_PARAMS+=( -e "PORT=${PORT}" )

DATABASE_PASSWORD="$(< docker/.secrets/db_password_frontend)"
DOCKER_ENV_PARAMS+=( -e "DATABASE_HOST=host.docker.internal" 
                     -e "DATABASE_PASSWORD=${DATABASE_PASSWORD}" )

docker run --rm -t --name number-plates-frontend \
  --env-file ./docker/frontend/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume ./common:/app/common \
  --volume ./frontend:/app/frontend \
  --publish ${PORT}:${PORT} \
  --add-host host.docker.internal:host-gateway \
  moujikov/number-plates-frontend
