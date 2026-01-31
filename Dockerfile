FROM python:3.14-slim

EXPOSE 8000/tcp

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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install cython setuptools numpy opencv_python scikit_image asyncio gitpython pycocotools pillow tqdm matplotlib scipy seaborn ipywidgets gevent termcolor scikit-learn albumentations fastapi orjson python-multipart uvicorn

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install ultralytics --no-deps 
RUN pip install pytorch_lightning==1.8.6 --no-deps

WORKDIR /project/number-plate-tests

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY utils utils
COPY test_images test_images
COPY self_check self_check
RUN python -m self_check

COPY . .

