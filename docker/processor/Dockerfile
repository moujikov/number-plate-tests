FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN <<EOF
    echo "--> Installing scheduler's own Python dependencies"
    set -ex -o pipefail

    pip install --upgrade pip
    pip install \
        aiofiles aiohttp aioshutil asyncio python-multipart tortoise-orm[asyncpg]
EOF


WORKDIR /app

COPY common common
COPY processor processor

ENTRYPOINT ["python", "-m", "processor"]
