#!/usr/bin/env bash

set -eu -o pipefail

PORT=8000
WORKERS=2

usage() {
  cat <<EOF
Usage: ./docker/scheduler/run.sh [--port <port>] [--token <token>] [--workers <number>]

Options:
  --port, -p            Port to run the server on (default: ${PORT})
  --token, -t           Access token for authentication (looked up in secrets if omitted)
  --workers, -w         Number of workers to add (default: ${WORKERS}).
                        Workers are presumed to run locally on scheduler's port + {1...N}.
                        Access tokens are looked up in secrets
  --help, -h            Show this help

Examples:
  ./docker/scheduler/run.sh
  ./docker/scheduler/run.sh --token _TOKEN12345 --workers 3
  ./docker/scheduler/run.sh --port 8001 --workers 2
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
      ;;
    --token|-t)
      ACCESS_TOKEN=${2:-}
      shift 2
      ;;
    --token=*)
      ACCESS_TOKEN=${1#*=}
      shift
      ;;
    --workers|-w)
      WORKERS=${2:-}
      shift 2
      ;;
    --workers=*)
      WORKERS=${1#*=}
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

DOCKER_ENV_PARAMS+=( -e "PORT=${PORT}" )

if [[ -z "${ACCESS_TOKEN:-}" ]]; then
  secret_file="docker/.secrets/scheduler_access_token"
  if [[ -f "$secret_file" ]]; then
      ACCESS_TOKEN="$(< "$secret_file")"
  fi
fi

if [[ -n "${ACCESS_TOKEN:-}" ]]; then
  DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${ACCESS_TOKEN}" )
fi

for i in $(seq 1 $WORKERS); do
  WORKER_PORT=$(( PORT + i ))
  WORKER_ACCESS_TOKEN=$(< "docker/.secrets/worker-${i}_access_token")
  DOCKER_ENV_PARAMS+=(
    -e "WORKER_URL_${i}=http://host.docker.internal:${WORKER_PORT}" 
    -e "WORKER_ACCESS_TOKEN_${i}=${WORKER_ACCESS_TOKEN}" 
    )
done

docker run --rm -t --name number-plates-scheduler \
  --env-file ./docker/scheduler/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume .:/app \
  --publish ${PORT}:${PORT} \
  --add-host host.docker.internal:host-gateway \
  moujikov/number-plates-scheduler
