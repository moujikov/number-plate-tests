#!/usr/bin/env bash

set -eu -o pipefail

CHECK_PERIOD=1h


usage() {
  cat <<EOF
Usage: ./docker/primeskud.web/run.sh [--check-period <period>] [--web-login <login>] ...

Options:
  --check-period, -cp     New data request frequency (e.g. 5m, 1h, default: ${CHECK_PERIOD})
  --web-login, -wl        Login for Prime Skud web interface
  --web-password, -wp     Password for Prime Skud web interface (looked up in secrets if omitted)
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
      WEB_LOGIN=${2:-}
      shift 2
      ;;
    --web-login=*)
      WEB_LOGIN=${1#*=}
      shift
      ;;
    --web-password|-wp)
      WEB_PASSWORD=${2:-}
      shift 2
      ;;
    --web-password=*)
      WEB_PASSWORD=${1#*=}
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

if [[ -z "${WEB_PASSWORD:-}" ]]; then
  secret_file="docker/.secrets/primeskud_web_password"
  if [[ -f "$secret_file" ]]; then
      WEB_PASSWORD="$(< "$secret_file")"
  fi
fi

if [[ -n "${WEB_LOGIN:-}" ]]; then
  DOCKER_ENV_PARAMS+=( -e "WEB_LOGIN=${WEB_LOGIN}" )
fi

if [[ -n "${WEB_PASSWORD:-}" ]]; then
  DOCKER_ENV_PARAMS+=( -e "WEB_PASSWORD=${WEB_PASSWORD}" )
fi

DATABASE_PASSWORD="$(< docker/.secrets/db_password_skud)"
DOCKER_ENV_PARAMS+=( -e "DATABASE_TYPE=postgres" -e "DATABASE_HOST=host.docker.internal" -e "DATABASE_PORT=5432" -e "DATABASE_NAME=number_plates" -e "DATABASE_USER=skud" -e "DATABASE_PASSWORD=${DATABASE_PASSWORD}" )


docker run --rm -t --name number-plates-primeskud.web \
  --env-file ./docker/primeskud.web/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume ./common:/app/common \
  --volume ./database:/app/database \
  --volume ./skud/backend:/app/skud/backend \
  --volume ./skud/primeskud_web:/app/skud/primeskud_web \
  --add-host host.docker.internal:host-gateway \
  moujikov/number-plates-primeskud.web
