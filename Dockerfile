FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PIP_NO_CACHE_DIR=false

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    manpages-dev \
    libglib2.0-0 \
    libgl1 \
    git \
    python3-setuptools \
    python3-wheel \
    libturbojpeg0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install cython setuptools numpy opencv_python scikit_image asyncio gitpython pycocotools ujson pillow tqdm matplotlib scipy seaborn ipywidgets gevent termcolor scikit-learn albumentations

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install torchvision --index-url https://download.pytorch.org/whl/cpu

RUN pip install ultralytics --no-deps 
RUN pip install pytorch_lightning==1.8.6 --no-deps

WORKDIR /project/number-plate-tests

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pipelines pipelines
COPY test_images test_images
COPY self_check self_check
RUN python -m self_check

COPY . .

