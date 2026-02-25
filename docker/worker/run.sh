#!/usr/bin/env bash

set -eu -o pipefail

PORT=8000
COUNTRIES="RU"
REQUESTS=1

usage() {
	cat <<EOF
Usage: ./docker/worker/run.sh [--port <port>] [--token <token>] [--requests <requests>] [--countries <countries>]

Options:
  --port, -p        Port to run the server on (default: ${PORT}).
  --token, -t       Access token for authentication.
  --requests, -r    Maximum number of concurrent requests (default: ${REQUESTS}).
  --countries, -c   Supported countries (default: ${COUNTRIES}; options: ALL | RU,BY,AM...).
  --help, -h        Show this help

Examples:
  ./docker/worker/run.sh
  ./docker/worker/run.sh --port 8001 --countries RU,BY,AM,GE
  ./docker/worker/run.sh --token _TOKEN12345 --requests 10 --countries ALL
EOF
}

DOCKER_ENV_PARAMS=()

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
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${2:-}" )
			shift 2
			;;
		--token=*)
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${1#*=}" )
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

DOCKER_ENV_PARAMS+=( 
	-e "PORT=${PORT}" \
	-e "DETECT_COUNTRIES=${COUNTRIES}" \
	-e "MAX_CONCURRENT_REQUESTS=${REQUESTS}" )

docker run --rm -t --name number-plates-worker \
	--env-file ./docker/worker/.env \
	${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
	--volume .:/app \
	--publish ${PORT}:${PORT} \
	moujikov/number-plates-worker
