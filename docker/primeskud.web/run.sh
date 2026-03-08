#!/usr/bin/env bash

set -eu -o pipefail

CHECK_PERIOD=1m
PRIME_SKUD_URL=https://prime-skud.ru


usage() {
  cat <<EOF
Usage: ./docker/primeskud.web/run.sh [--scheduler-port <port>] [--scheduler-token <token>] ...

Options:
  --check-period, -cp     New data request frequency (e.g. 5m, 1h, default: 1m).
  --web-login, -wl        Login for Prime Skud web interface.
  --web-password, -wp     Password for Prime Skud web interface.
  --help, -h              Show this help

Examples:
  ./docker/primeskud.web/run.sh
  ./docker/primeskud.web/run.sh --scheduler-port 8001 --scheduler-token _TOKEN12345
EOF
}

DOCKER_ENV_PARAMS=( -e "PYTHONDEVMODE=1" -e "LOG_LEVEL=DEBUG")

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-period|-cp)
      CHECK_PERIOD=${2:-}
      shift 2
      ;;
    --check-period=*)
      CHECK_PERIOD=${1#*=}
      shift
      ;;
    --web-login|-wl)
      DOCKER_ENV_PARAMS+=( -e "WEB_LOGIN=${2:-}" )
      shift 2
      ;;
    --web-login=*)
      DOCKER_ENV_PARAMS+=( -e "WEB_LOGIN=${1#*=}" )
      shift
      ;;
    --web-password|-wp)
      DOCKER_ENV_PARAMS+=( -e "WEB_PASSWORD=${2:-}" )
      shift 2
      ;;
    --web-password=*)
      DOCKER_ENV_PARAMS+=( -e "WEB_PASSWORD=${1#*=}" )
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
      ;;
  esac
done


DOCKER_ENV_PARAMS+=( -e "CHECK_PERIOD=${CHECK_PERIOD}" )
DOCKER_ENV_PARAMS+=( -e "PRIME_SKUD_URL=${PRIME_SKUD_URL}" )
DOCKER_ENV_PARAMS+=( -e "DATABASE_URL=postgres://skud:__POSTGRES_SKUD_PASSWORD__@host.docker.internal:5432/number_plates" )


docker run --rm -t --name number-plates-primeskud.web \
  --env-file ./docker/primeskud.web/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume ./common:/app/common \
  --volume ./database:/app/database \
  --volume ./skud/primeskud_web:/app/skud/primeskud_web \
  --mount type=bind,src=".secrets/primeskud_web_password.txt",dst=/run/secrets/web_password,readonly \
  --add-host host.docker.internal:host-gateway \
  moujikov/number-plates-primeskud.web
