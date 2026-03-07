import asyncio
import os

from common.logging import logger
from . import CAMERAS_DIR, PROCESS_AT_ONCE
from .image import InputImage
from .session import SchedulerSession
from .task import DetectionTask


class ImagesProcessor:
  def __init__(self, session: SchedulerSession):
    self._session = session
    self._processing : dict[str, asyncio.Task] = {}

  # Do not await inside this method to avoid race conditions with file listings
  async def process_new_images(self):
    free_slots = max(PROCESS_AT_ONCE - len(self._processing), 0)
    if free_slots == 0:
      return

    cameras = sorted(os.listdir(CAMERAS_DIR))
    images = []
    for camera in cameras:
      upload = os.path.join(CAMERAS_DIR, camera, 'upload')
      if os.path.isdir(upload):
        images.extend([InputImage(camera, file) 
                       for file in os.scandir(upload)
                       if file.is_file()
                          and file.path not in self._processing
                          and (file.name.lower().endswith('.jpg') 
                               or file.name.lower().endswith('.jpeg'))])

    if images: 
      images.sort()
      images_to_process = images[:free_slots]
      logger.debug(
        f'Got {len(images)} new {"image" if len(images) == 1 else "images"}, '
        f'processing {len(images_to_process)}: '
        f'[{", ".join([image.full_name for image in images_to_process])}]')
      for image in images_to_process:
        detection = DetectionTask(self._session, image)
        task = asyncio.create_task(detection.fullfill())
        self._processing[image.path] = task
        task.add_done_callback(lambda t, path=image.path: self._processing.pop(path))
