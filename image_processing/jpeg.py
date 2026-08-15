from typing import List
from numpy import ndarray
from turbojpeg import TurboJPEG
from turbojpeg import TJPF_RGB

__jpeg = TurboJPEG()


def read_image(bytes: bytes) -> ndarray:
  return __jpeg.decode(bytes, TJPF_RGB)


def read_local_images(files: List[str] | str) -> List[ndarray]:
  images = []
  if isinstance(files, str): files = [files]
  for file in files:
    with open(file, "rb") as f:
      images.append(read_image(f.read()))
  return images
