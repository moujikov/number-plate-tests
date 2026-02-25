#!/usr/bin/env bash

set -eu -o pipefail

PORT=8000

usage() {
	cat <<EOF
Usage: ./docker/scheduler/run.sh [--port <port>] [--token <token>] [--worker-port <port>] [--worker-token <token>] ...

Options:
  --port, -p		    		Port to run the server on (default: ${PORT}).
  --token, -t		    		Access token for authentication.
	--worker-port, -wp		Add worker runnning locally on the specified port (repeatable).
	--worker-token, -wt		Add worker access token for authentication (repeat for each worker).
  --help, -h		    		Show this help

Examples:
  ./docker/scheduler/run.sh
  ./docker/scheduler/run.sh --port 8001 --token _TOKEN12345
EOF
}

DOCKER_ENV_PARAMS=()
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
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${2:-}" )
			shift 2
			;;
		--token=*)
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${1#*=}" )
			shift
			;;
		--worker-port|-wp)
			url_id=$((url_id+1))
			DOCKER_ENV_PARAMS+=( -e "WORKER_URL_${url_id}=http://host.docker.internal:${2:-}" )
			shift 2
			;;
		--worker-port=*)
			url_id=$((url_id+1))
			DOCKER_ENV_PARAMS+=( -e "WORKER_URL_${url_id}=http://host.docker.internal:${1#*=}" )
			shift
			;;
		--worker-token|-wt)
			DOCKER_ENV_PARAMS+=( -e "WORKER_ACCESS_TOKEN_${url_id}=${2:-}" )
			shift 2
			;;
		--worker-token=*)
			DOCKER_ENV_PARAMS+=( -e "WORKER_ACCESS_TOKEN_${url_id}=${1#*=}" )
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

DOCKER_ENV_PARAMS+=( -e "PORT=${PORT}" )

docker run --rm -t --name number-plates-scheduler \
	--env-file ./docker/scheduler/.env \
	${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
	--volume .:/app \
	--publish ${PORT}:${PORT} \
	--add-host host.docker.internal:host-gateway \
	moujikov/number-plates-scheduler
