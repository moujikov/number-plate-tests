FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install cython setuptools numpy opencv_python scikit_image asyncio gitpython pycocotools pillow tqdm matplotlib scipy seaborn ipywidgets gevent termcolor scikit-learn albumentations aiohttp fastapi python-multipart uvicorn asgi-correlation-id

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install ultralytics --no-deps 
RUN pip install pytorch_lightning --no-deps

RUN pip install git+https://github.com/lilohuang/PyTurboJPEG.git
RUN pip install git+https://github.com/moujikov/ria-com_nomeroff-net.git


WORKDIR /app

COPY common common
COPY image_processing image_processing
COPY self_check self_check

# Preload all necessary models and check basic detection functionality
RUN python -m self_check

COPY rest_server/common rest_server/common
COPY rest_server/worker rest_server/worker

ENTRYPOINT ["python", "-m", "rest_server.worker"]

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --start-interval=1s --retries=3 \
    CMD curl --fail http://${BIND:-localhost}:${PORT:-8000}/healthcheck || exit 1
