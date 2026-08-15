#!/usr/bin/env bash

set -eu -o pipefail

HOST="localhost"
PORT="21"

usage() {
  cat <<EOF
Usage: ./_test/upload.sh [--base-url <url>] [--file <path> ...] [--token <token>]

Options:
  --host, -h        FTP host (default: ${HOST})
  --port, -p        FTP port (default: ${PORT})
  --user, -u        FTP user to authenticate with
  --password, -w    FTP password (looked up in secrets if omitted) 
  --file, -f        Directory or single image file to upload (repeatable).
                    If ommitted a full set of local test images will be used
  --help, -h        Show this help

Examples:
  ./_test/upload.sh
  ./_test/upload.sh --host ftp.somehost.com --user camera-1 --file ./some.jpg
  ./_test/upload.sh --user camera-1 --file ./one.jpg --file ./two.jpg
EOF
}

FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host|-h)
      HOST="${2:-}"
      shift 2
      ;;
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --port|-p)
      PORT="${2:-}"
      shift 2
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --user|-u)
      USER="${2:-}"
      shift 2
      ;;
    --user=*)
      USER="${1#*=}"
      shift
      ;;
    --password|-w)
      PASSWORD="${2:-}"
      shift 2
      ;;
    --password=*)
      PASSWORD="${1#*=}"
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
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$USER" ]]; then
  echo "No user provided."
  echo "Use --user/-u parameter." >&2
  usage >&2
  exit 2
fi

if [[ -z "${PASSWORD+set}" ]]; then
  secret_file="docker/.secrets/ftp_${USER}_password"
  if [[ ! -f "$secret_file" ]]; then
    echo "No secret found in '$secret_file' and no password explicitly provided."
    echo "Use --password/-p parameter." >&2
    usage >&2
    exit 2
  fi

  PASSWORD="$(< "$secret_file")"
fi

CURL_ARGS=( --user "$USER:$PASSWORD" )

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
  echo "No files provided."
  echo "Use --file/-f parameter." >&2
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
  CURL_ARGS+=( "ftp://${HOST}:${PORT}" --upload-file "$f" )
done


curl -v ${CURL_ARGS[@]+"${CURL_ARGS[@]}"}
