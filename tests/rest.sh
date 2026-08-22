#!/usr/bin/env bash

set -euo pipefail

DEFAULT_HOST="http://localhost"
DEFAULT_PORT="8000"

usage() {
  cat <<EOF
Usage: ./_test/rest.sh [--base-url <url>] [--file <path> ...] [--token <token>]

Options:
  --port, -p      Server port (default: ${DEFAULT_PORT})
  --url, -u       Server URL (default: ${DEFAULT_HOST}:${DEFAULT_PORT}, overrides --port)
  --file, -f      Directory or single image file to upload (repeatable)
                  If ommitted a full set of local test images will be used
  --token, -t     Access token for authentication
                  Also accepts file path to read token from
  --help, -h      Show this help

Examples:
  ./_test/rest.sh
  ./_test/rest.sh all --port 8080
  ./_test/rest.sh --url http://somehost:8080/somepath
  ./_test/rest.sh ru --file ./some.jpg
  ./_test/rest.sh all --file ./_test/images --token _TOKEN12345 --details full
EOF
}

BASE_URL=""
TOKEN=""
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
    --port|-p)
      if [[ -z "$BASE_URL" ]]; then
        BASE_URL="${DEFAULT_HOST}:${2:-}"
      fi
      shift 2
      ;;
    --port=*)
      if [[ -z "$BASE_URL" ]]; then
        BASE_URL="${DEFAULT_HOST}:${1#*=}"
      fi
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
    --token|-t)
      TOKEN="${2:-}"
      shift 2
      ;;
    --token=*)
      TOKEN="${1#*=}"
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

if [[ -z "$BASE_URL" ]]; then
  BASE_URL="${DEFAULT_HOST}:${DEFAULT_PORT}"
fi

CURL_ARGS=()

if [[ -n "$TOKEN" ]]; then
  if [[ -f "$TOKEN" ]]; then
    TOKEN="$(< "$TOKEN")"
  fi
  CURL_ARGS+=( -H "Authorization: Bearer ${TOKEN}" )
fi


# If no files provided, use all local test images
if [[ ${#FILES[@]} -eq 0 ]]; then
  FILES=(./_test/images)
fi

# Populate FILES array with files from all directories
for d in "${FILES[@]}"; do
  if [[ -d "$d" ]]; then
    while IFS= read -r -d '' f; do
      FILES+=("$f")
    done < <(find "$d" -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -print0 | sort -z)
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files provided. Use --file/-f parameter." >&2
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
  CURL_ARGS+=( -F "images=@${f};filename=\"$f\"" )
done

start=`date +%s.%N`

curl -v "${BASE_URL}/detect" ${CURL_ARGS[@]+"${CURL_ARGS[@]}"} | jq

end=`date +%s.%N`
runtime=$( echo "scale=2; ($end - $start) / 1" | bc -l )
echo "Done in: ${runtime} sec"
