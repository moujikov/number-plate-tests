#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: ./run-scheduler-server.sh [--port <port>] [--token <token>] [--worker-port <port>] [--worker-token <token>] ...

Options:
  --port, -p		    		Port to run the server on.
  --token, -t		    		Access token for authentication.
	--worker-port, -wp		Add worker runnning locally on the specified port (repeatable).
	--worker-token, -wt		Add worker access token for authentication (repeat for each worker).
  --help, -h		    		Show this help

Examples:
  ./run-scheduler-server.sh
  ./run-scheduler-server.sh --port 8000 --token _TOKEN12345
EOF
}

DOCKER_ENV_PARAMS=()
PORT=8000
url_id=0

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
		--worker-port|-wp)
			url_id=$((url_id+1))
			DOCKER_ENV_PARAMS+=( -e "WORKER_URL_#${url_id}=http://host.docker.internal:${2:-}" )
			shift 2
			;;
		--worker-port=*)
			url_id=$((url_id+1))
			DOCKER_ENV_PARAMS+=( -e "WORKER_URL_#${url_id}=http://host.docker.internal:${1#*=}" )
			shift
			;;
		--worker-token|-wt)
			DOCKER_ENV_PARAMS+=( -e "WORKER_ACCESS_TOKEN_#${url_id}=${2:-}" )
			shift 2
			;;
		--worker-token=*)
			DOCKER_ENV_PARAMS+=( -e "WORKER_ACCESS_TOKEN_#${url_id}=${1#*=}" )
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
	${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
	-v .:/number-plates \
	-p ${PORT}:${PORT} \
	--add-host host.docker.internal:host-gateway \
	moujikov/number-plate-tests \
	python -m rest_server.scheduler
