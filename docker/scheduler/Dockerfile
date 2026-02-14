FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install asyncio aiohttp fastapi python-multipart uvicorn asgi-correlation-id


WORKDIR /app

COPY common common
COPY rest_server/common rest_server/common
COPY rest_server/scheduler rest_server/scheduler

ENTRYPOINT ["python", "-m", "rest_server.scheduler"]

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --start-interval=1s --retries=3 \
    CMD curl --fail http://${BIND:-localhost}:${PORT:-8000}/healthcheck || exit 1
