#!/usr/bin/env bash
set -eu -o pipefail

CAMERAS=2
WORKERS=2

usage() {
	cat <<EOF
Usage: ./docker/gen-secrets.sh [--cameras <count> --workers <count>]

Options:
  --cameras, -c		    	Number of cameras (default: ${CAMERAS})
  --workers, -w         Number of workers (default: ${WORKERS})
  --help, -h		    		Show this help

Examples:
  ./docker/gen-secrets.sh
  ./docker/gen-secrets.sh --cameras 3 --workers 6
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--cameras|-c)
			CAMERAS="${2:-}"
			shift 2
			;;
		--cameras=*)
			CAMERAS="${1#*=}"
			shift
			;;
		--workers|-w)
			WORKERS="${2:-}"
			shift 2
			;;
		--workers=*)
			WORKERS="${1#*=}"
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



generate_secret() {
  local file="$1"
  local length=${2:-16}
  local prefix="${3:-}"
  local permissions="${4:-0600}"

  if [ -f "$file" ]; then
    echo "File '$file' already exists."
    echo "Delete it explicitly to regenerate. Skipping..."; echo
  else
    install -m "$permissions" /dev/null "$file"
    printf "$prefix" >> "$file"
    (
      set +o pipefail   # Disable pipefail since cat will fail after SIGPIPE when head exits
      cat /dev/random | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c $length >> "$file"
    ) || exit $?
    echo "Generated secret in '$file'"; echo
  fi
}


generate_secret docker/.secrets/db_password_postgres 32 __postgres_  
generate_secret docker/.secrets/db_password_processor 32 __processor_ 0644
generate_secret docker/.secrets/db_password_skud 32 __skud_ 0644
generate_secret docker/.secrets/db_password_frontend 32 __frontend_ 0644

generate_secret docker/.secrets/scheduler_access_token 48 __scheduler_

for i in $(seq 1 $WORKERS); do
  generate_secret docker/.secrets/worker-${i}_access_token 48 __worker_${i}_
done

for i in $(seq 1 $CAMERAS); do
  generate_secret docker/.secrets/ftp_camera-${i}_password 10
done


primeskud_web_password='docker/.secrets/primeskud_web_password'
if [ -f "$primeskud_web_password" ]; then
  echo "Prime Skud web password already exists."
  echo "Delete '$primeskud_web_password' file explicitly to update. Skipping..."; echo
else
  read -s -r -p "Enter Prime Skud web password: " password
  if [ -n "$password" ]; then
    install -m 0600 /dev/null "$primeskud_web_password"
    echo "$password" >> "$primeskud_web_password"; echo
    echo "Saved Prime Skud web password to '$primeskud_web_password'"; echo
    unset password
  else
    echo "No password entered. Skipping Prime Skud web password generation."; echo
  fi
fi
