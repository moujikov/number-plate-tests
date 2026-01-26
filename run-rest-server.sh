#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: ./run-rest-server.sh [--token <token>]

Options:
  --token, -t   Access token for authentication.
  --help, -h    Show this help

Examples:
  ./run-rest-server.sh
  ./run-rest-server.sh --token _TOKEN12345
EOF
}

DOCKER_ENV_PARAMS=()

while [[ $# -gt 0 ]]; do
	case "$1" in
		--token|-t)
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${2:-}" )
			shift 2
			;;
		--token=*)
			DOCKER_ENV_PARAMS+=( -e "ACCESS_TOKEN=${1#*=}" )
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
	"${DOCKER_ENV_PARAMS[@]}" \
	-v .:/project/number-plate-tests \
	-p 8000:8000 \
	moujikov/number-plate-tests \
	python -m rest_server_test
