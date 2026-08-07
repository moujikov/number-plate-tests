FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN <<EOF
    echo "--> Installing general system dependencies"
    set -ex -o pipefail

    apt-get update 
    apt-get install -y --no-install-recommends curl

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    echo "--> Installing frontend's own Python dependencies"
    set -ex -o pipefail

    pip install --upgrade pip
    pip install django uvicorn
EOF


WORKDIR /app

COPY common common
COPY frontend frontend

ENTRYPOINT ["python", "-m", "frontend"]

# HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --start-interval=1s --retries=3 \
#     CMD curl --fail http://${BIND:-localhost}:${PORT:-80}/healthcheck || exit 1
