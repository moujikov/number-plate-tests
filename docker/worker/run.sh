#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: ./docker/worker/run.sh [--port <port>] [--token <token>] [--requests <requests>]

Options:
  --port, -p		    Port to run the server on.
	--token, -t		    Access token for authentication.
  --requests, -r	  Maximum number of concurrent requests.
	--countries, -c  	Supported countries (default: RU; options: RU_BY, ALL).
  --help, -h		    Show this help

Examples:
  ./docker/worker/run.sh
  ./docker/worker/run.sh --port 8000
  ./docker/worker/run.sh --token _TOKEN12345 --requests 10 --countries ALL
EOF
}

DOCKER_ENV_PARAMS=()
COUNTRIES=""
PORT=8000

while [[ $# -gt 0 ]]; do
	case "$1" in
		--port|-p)
			DOCKER_ENV_PARAMS+=( -e "PORT=${2:-}" )
			PORT="${2:-}"
			shift 2
			;;
		--port=*)
			DOCKER_ENV_PARAMS+=( -e "PORT=${1#*=}" )
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
      DOCKER_ENV_PARAMS+=( -e "MAX_CONCURRENT_REQUESTS=${2:-}" )
      shift 2
      ;;
    --requests=*)
      DOCKER_ENV_PARAMS+=( -e "MAX_CONCURRENT_REQUESTS=${1#*=}" )
      shift
      ;;
		--countries|-c)
      DOCKER_ENV_PARAMS+=( -e "DETECT_COUNTRIES=${2:-}" )
      shift 2
      ;;
    --countries=*)
      DOCKER_ENV_PARAMS+=( -e "DETECT_COUNTRIES=${1#*=}" )
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


docker run --rm -t \
	--env-file ./docker/worker/.env \
	${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
	-v .:/app \
	-p ${PORT}:${PORT} \
	moujikov/number-plates-worker
