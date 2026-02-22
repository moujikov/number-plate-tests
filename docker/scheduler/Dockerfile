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
    echo "--> Installing scheduler's own Python dependencies"
    set -ex -o pipefail

    pip install --upgrade pip
    pip install \
        aiohttp asgi-correlation-id asyncio fastapi python-multipart uvicorn
EOF


WORKDIR /app

COPY common common
COPY rest_server/common rest_server/common
COPY rest_server/scheduler rest_server/scheduler

ENTRYPOINT ["python", "-m", "rest_server.scheduler"]

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --start-interval=1s --retries=3 \
    CMD curl --fail http://${BIND:-localhost}:${PORT:-8000}/healthcheck || exit 1
