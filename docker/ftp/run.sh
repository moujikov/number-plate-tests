#!/usr/bin/env bash

set -euo pipefail

PORT=21

usage() {
	cat <<EOF
Usage: ./docker/ftp/run.sh [--port <port>]

Options:
  --port, -p		    		Port to run the server on (default: ${PORT}).
  --help, -h		    		Show this help

Examples:
  ./docker/ftp/run.sh
  ./docker/ftp/run.sh --port 2121
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

# Add mock users
DOCKER_ENV_PARAMS+=( -e "FTP_USER_1=camera-1" -e "FTP_PASSWORD_1=pass1" )
DOCKER_ENV_PARAMS+=( -e "FTP_USER_2=camera-2" -e "FTP_PASSWORD_2=pass2" )

# Add test passive ports range
PASSIVE_PORTS="30001-30005"
DOCKER_ENV_PARAMS+=( -e "PASSIVE_PORTS=${PASSIVE_PORTS}" )

docker run --rm -t --name number-plates-ftp \
	--env-file ./docker/ftp/.env \
	${DOCKER_ENV_PARAMS[@]+"${DOCKER_ENV_PARAMS[@]}"} \
	--volume ./docker/ftp/proftpd.conf:/etc/proftpd/proftpd.conf \
	--volume ./docker/ftp/entrypoint.sh:/entrypoint.sh \
	--volume number-plates_cameras:/home \
	--volume number-plates_logs_ftp-server:/var/log/proftpd \
	--publish ${PORT}:${PORT} \
	--publish ${PASSIVE_PORTS}:${PASSIVE_PORTS} \
	moujikov/number-plates-ftp
