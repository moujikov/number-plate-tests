FROM python:3.14-slim

EXPOSE 8000/tcp

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip
RUN pip install asyncio aiohttp fastapi python-multipart uvicorn asgi-correlation-id


WORKDIR /app

COPY common common
COPY rest_server/common rest_server/common
COPY rest_server/scheduler rest_server/scheduler

ENTRYPOINT ["python", "-m", "rest_server.scheduler"]
