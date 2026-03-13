#!/usr/bin/env bash

set -eu -o pipefail

DEFAULT_PORT=8000
REQUESTS=1
COUNTRIES="RU"

usage() {
  cat <<EOF
Usage: ./docker/worker/run.sh [--port <port>] [--token <token>] [--requests <requests>] [--countries <countries>] [--number <number>]

Options:
  --port, -p        Port to run the server on (default: ${DEFAULT_PORT})
  --token, -t       Access token for authentication (looked up in secrets if omitted)
  --number, -n      Worker number.
                    If no explicit port, sets port to ${DEFAULT_PORT} + <n>
                    If no explicit access token, sets token to secret number <n>
  --requests, -r    Maximum number of concurrent requests (default: ${REQUESTS})
  --countries, -c   Supported countries (default: ${COUNTRIES}; options: ALL | RU,BY,AM...)
  --help, -h        Show this help

Examples:
  ./docker/worker/run.sh
  ./docker/worker/run.sh --port 8001 --countries RU,BY,AM,GE
  ./docker/worker/run.sh --token _TOKEN12345 --requests 10 --countries ALL
EOF
}

DOCKER_ENV_PARAMS=( -e "PYTHONDEVMODE=1" -e "LOG_LEVEL=DEBUG" )

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
      ACCESS_TOKEN="${2:-}"
      shift 2
      ;;
    --token=*)
      ACCESS_TOKEN="${1#*=}"
      shift
      ;;
    --number|-n)
      WORKER_NUMBER="${2:-}"
      shift 2
      ;;
    --number=*)
      WORKER_NUMBER="${1#*=}"
      shift
      ;;
    --requests|-r)
      REQUESTS="${2:-}"
      shift 2
      ;;
    --requests=*)
      REQUESTS="${1#*=}"
      shift
      ;;
    --countries|-c)
      COUNTRIES="${2:-}"
      shift 2
      ;;
    --countries=*)
      COUNTRIES="${1#*=}"
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

if [[ -z "${PORT:-}" ]]; then
  if [[ -n "${WORKER_NUMBER:-}" ]]; then
    PORT=$(( DEFAULT_PORT + WORKER_NUMBER ))
  else
    PORT=$DEFAULT_PORT
  fi
fi

DOCKER_ENV_PARAMS+=( 
  -e "PORT=${PORT}" \
  -e "DETECT_COUNTRIES=${COUNTRIES}" \
  -e "MAX_CONCURRENT_REQUESTS=${REQUESTS}" )

if [[ -z "${ACCESS_TOKEN:-}" ]]; then
  INDEX=${WORKER_NUMBER:-1}
  secret_file="docker/.secrets/worker-${INDEX}_access_token"
  if [[ -f "$secret_file" ]]; then
    ACCESS_TOKEN="$(< "$secret_file")"
  fi
fi

if [[ -n "${ACCESS_TOKEN:-}" ]]; then
  DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${ACCESS_TOKEN}" )
fi

docker run --rm -t --name number-plates-worker${WORKER_NUMBER:+-${WORKER_NUMBER}} \
  --env-file ./docker/worker/.env \
  ${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
  --volume ./common:/app/common \
  --volume ./image_processing:/app/image_processing \
  --volume ./rest_server/common:/app/rest_server/common \
  --volume ./rest_server/worker:/app/rest_server/worker \
  --publish ${PORT}:${PORT} \
  moujikov/number-plates-worker
