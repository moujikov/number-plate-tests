FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow

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

RUN python3 -m pip install --upgrade pip

# WORKDIR /project

RUN python3 -m pip install cython setuptools numpy opencv_python scikit_image asyncio gitpython pycocotools ujson pillow tqdm matplotlib scipy seaborn ipywidgets gevent termcolor scikit-learn albumentations

RUN python3 -m pip install "torch>=1.12" "torchvision>=0.13" --index-url https://download.pytorch.org/whl/cpu

RUN python3 -m pip install "ultralytics>=8.3.12" "pytorch_lightning==1.8.6"

RUN python3 -m pip install "git+https://github.com/moujikov/ria-com_nomeroff-net.git"

WORKDIR /project/
COPY ./self-check ./self-check
RUN python3 -m self-check

WORKDIR /project/number-plate-tests
