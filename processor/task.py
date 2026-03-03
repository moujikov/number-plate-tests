import os
from aiofiles import os as aio_os
import aiofiles
import aioshutil
import uuid

from common.logging import logger
from . import CAMERAS_DIR, IMAGES_DIR
from .image import InputImage
from .session import SchedulerSession


class Task:
  async def fullfill(self):
    pass

class DetectionTask(Task):
  def __init__(self, session: SchedulerSession, image: InputImage):
    self._session = session
    self._image = image

  async def fullfill(self):
    async with aiofiles.open(self._image.path, mode='rb') as file:
      contents = await file.read()
    
    results = await self._session.detect(f'{self._image.full_name}', contents)

    if "images" in results:
      logger.debug(f'Detection results for {self._image.full_name} – {results}')
      date_subdir = self._image.date_str
      date_subdir_file = os.path.join(date_subdir, f'{uuid.uuid4()}.jpg')

      await aio_os.makedirs(os.path.join(IMAGES_DIR, date_subdir), exist_ok=True)
      await aioshutil.move(self._image.path, os.path.join(IMAGES_DIR, date_subdir_file))
      logger.info(f'Processed {self._image.full_name}, saved to {date_subdir_file}')
    else:
      logger.warning(f'Detection failed for {self._image.full_name} – {results}')
      failed_dir = os.path.join(CAMERAS_DIR, self._image.camera, 'failed')
      await aio_os.makedirs(failed_dir, exist_ok=True)
      await aioshutil.move(self._image.path, os.path.join(failed_dir, self._image.name))
      logger.info(f"Moved {self._image.full_name} to camera's failed images")
      return
