import asyncio
from typing import List
from numpy import ndarray
from turbojpeg import TurboJPEG
from turbojpeg import TJPF_RGB

__jpeg = TurboJPEG()


async def read_image_async(jpg_image: bytes) -> ndarray:
  return await asyncio.to_thread(read_image, jpg_image)


def read_image(bytes: bytes) -> ndarray:
  return __jpeg.decode(bytes, TJPF_RGB)


def read_local_image(file: str) -> ndarray:
  with open(file, "rb") as f:
    return read_image(f.read())


def read_local_images(files: List[str]) -> List[ndarray]:
  images = []
  for file in files:
    with open(file, "rb") as f:
      images.append(read_image(f.read()))
  return images
