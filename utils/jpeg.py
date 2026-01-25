from typing import List
from turbojpeg import TurboJPEG
from turbojpeg import TJPF_RGB

__jpeg = TurboJPEG()


def read_image(bytes: bytes):
  return __jpeg.decode(bytes, TJPF_RGB)


def read_local_images(files: List[str]):
  images = []
  for file in files:
    with open(file, "rb") as f:
      images.append(read_image(f.read()))
  return images
