#!/usr/bin/env bash

set -eu -o pipefail

SCHEDULER_PORT=8000
PROCESS_AT_ONCE=3

usage() {
  cat <<EOF
Usage: ./docker/processor/run.sh [--scheduler-port <port>] [--scheduler-token <token>] ...

Options:
  --scheduler-port, -sp     Add scheduler running locally on the specified port (default: ${SCHEDULER_PORT})
  --scheduler-token, -st    Add scheduler access token for authentication (looked up in secrets if omitted)
  --process-at-once, -pa    Number of tasks to process at once (default: 3)
  --help, -h                Show this help

Examples:
  ./docker/processor/run.sh
  ./docker/processor/run.sh --scheduler-port 8001 --scheduler-token _TOKEN12345
EOF
}

DOCKER_ENV_PARAMS=( -e "PYTHONDEVMODE=1" -e "LOG_LEVEL=DEBUG" )

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scheduler-port|-sp)
      SCHEDULER_PORT=${2:-}
      shift 2
      ;;
    --scheduler-port=*)
      SCHEDULER_PORT=${1#*=}
      shift
      ;;
    --scheduler-token|-st)
      SCHEDULER_ACCESS_TOKEN=${2:-}
      shift 2
      ;;
    --scheduler-token=*)
      SCHEDULER_ACCESS_TOKEN=${1#*=}
      shift
      ;;
    --process-at-once|-pa)
      PROCESS_AT_ONCE=${2:-}
      shift 2
      ;;
    --process-at-once=*)
      PROCESS_AT_ONCE=${1#*=}
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      shift
      ;;
  esac
done

CAMERAS_DIR=/var/local/cameras
IMAGES_DIR=/var/local/images

DOCKER_ENV_PARAMS+=( -e "CAMERAS_DIR=${CAMERAS_DIR}" )
DOCKER_ENV_PARAMS+=( -e "IMAGES_DIR=${IMAGES_DIR}" )
DOCKER_ENV_PARAMS+=( -e "PROCESS_AT_ONCE=${PROCESS_AT_ONCE}" )

if [[ -z "${SCHEDULER_ACCESS_TOKEN:-}" ]]; then
  secret_file="docker/.secrets/scheduler_access_token"
  if [[ -f "$secret_file" ]]; then
      SCHEDULER_ACCESS_TOKEN="$(< "$secret_file")"
  fi
fi

if [[ -n "${SCHEDULER_ACCESS_TOKEN:-}" ]]; then
  DOCKER_ENV_PARAMS+=( -e "SCHEDULER_ACCESS_TOKEN=${SCHEDULER_ACCESS_TOKEN}" )
fi

DATABASE_PASSWORD="$(< docker/.secrets/db_password_processor)"
DOCKER_ENV_PARAMS+=( -e "DATABASE_TYPE=postgres" -e "DATABASE_HOST=host.docker.internal" -e "DATABASE_PORT=5432" -e "DATABASE_NAME=number_plates" -e "DATABASE_USER=processor" -e "DATABASE_PASSWORD=${DATABASE_PASSWORD}" )


docker run --rm -t --name number-plates-processor \
  --env-file ./docker/processor/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume ./common:/app/common \
  --volume ./database:/app/database \
  --volume ./processor:/app/processor \
  --volume number-plates_cameras:${CAMERAS_DIR} \
  --volume number-plates_images:${IMAGES_DIR} \
  --add-host host.docker.internal:host-gateway \
  moujikov/number-plates-processor
