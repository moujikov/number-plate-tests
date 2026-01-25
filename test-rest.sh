#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: ./test-rest.sh [endpoint] [--base-url <url>] [--file <path> ...]

Options:
  endpoint      Which endpoint to call.
                Supported:
                  ru          -> /detect_ru (default)
                  all         -> /detect_all
  --url, -u     Server URL (default: http://127.0.0.1:8000)
  --file, -f    Directory or single image file to upload (repeatable).
                If ommitted a full set of local test images will be used.
  --help, -h    Show this help

Examples:
  ./test-rest.sh
  ./test-rest.sh all
  ./test-rest.sh --url http://localhost:8000
  ./test-rest.sh ru --file ./some.jpg
  ./test-rest.sh all -f ./test_images
EOF
}

BASE_URL="http://127.0.0.1:8000"
ENDPOINT="ru"
FILES=()

while [[ $# -gt 0 ]]; do
	case "$1" in
		--url|-u)
			BASE_URL="${2:-}"
			shift 2
			;;
		--url=*)
			BASE_URL="${1#*=}"
			shift
			;;
		--file|-f)
			FILES+=("${2:-}")
			shift 2
			;;
		--file=*)
			FILES+=("${1#*=}")
			shift
			;;
		--help|-h)
			usage
			exit 0
			;;
		*)
			ENDPOINT="$1"
      shift
			;;
	esac
done

case "$ENDPOINT" in
	ru)
		PATH_SUFFIX="/detect_ru"
    CURL_FORM_ARGS=( -F "details=none" )
		;;
	all)
		PATH_SUFFIX="/detect_all"
    CURL_FORM_ARGS=( -F "details=region" )
		;;
	*)
		echo "Unknown --endpoint value: $ENDPOINT" >&2
		usage >&2
		exit 2
		;;
esac

# If no files provided, use all local test images
if [[ ${#FILES[@]} -eq 0 ]]; then
  FILES=(./test_images)
fi

# Populate FILES array with files from all directories
for d in "${FILES[@]}"; do
  if [[ -d "$d" ]]; then
    while IFS= read -r -d '' f; do
      FILES+=("$f")
    done < <(find -s "$d" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0)
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files provided. Use --file/-f and/or --dir for $ENDPOINT." >&2
  usage >&2
  exit 2
fi

for f in "${FILES[@]}"; do
  if [[ -z "$f" ]] || [[ -d "$f" ]]; then
    continue
  fi
  if [[ ! -f "$f" ]]; then
    echo "File not found: $f" >&2
    exit 2
  fi
  CURL_FORM_ARGS+=( -F "files=@${f}" )
done

start=`date +%s.%N`

curl -v "${BASE_URL}${PATH_SUFFIX}" "${CURL_FORM_ARGS[@]}" | jq

end=`date +%s.%N`
runtime=$( echo "scale=2; ($end - $start) / 1" | bc -l )
echo "Done in: ${runtime} sec"
