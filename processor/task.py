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

    if 'images' in results:
      number_plates = self.extract_number_plates(results)
      if number_plates is not None:
        logger.info(f'Extracted number plates for {self._image.full_name} – {number_plates}')


        date_subdir = self._image.date_str
        date_subdir_file = os.path.join(date_subdir, f'{uuid.uuid4()}.jpg')

        await aio_os.makedirs(os.path.join(IMAGES_DIR, date_subdir), exist_ok=True)
        await aioshutil.move(self._image.path, os.path.join(IMAGES_DIR, date_subdir_file))
        logger.info(f'Processed {self._image.full_name}, saved to {date_subdir_file}')
      else:
        logger.warning(f'Unexpected detection results for {self._image.full_name} – {results}')
        await self.move_to_failed()
    else:
      logger.warning(f'Detection failed for {self._image.full_name} – {results}')
      await self.move_to_failed()


  def extract_number_plates(self, results: dict) -> list[str] | None:
    if 'images' not in results: return None
    results = results['images']
    if not isinstance(results, list) or len(results) != 1: return None
    results = results[0]
    if 'detections' not in results: return None
    detections = results['detections']
    if not isinstance(detections, list): return None
    number_plates = []
    for detection in detections:
      if 'text' not in detection: return None
      text = detection['text']
      if not isinstance(text, str): return None
      number_plates.append(text)
      
    return number_plates

    
  async def move_to_failed(self):
    failed_dir = os.path.join(CAMERAS_DIR, self._image.camera, 'failed')
    await aio_os.makedirs(failed_dir, exist_ok=True)
    await aioshutil.move(self._image.path, os.path.join(failed_dir, self._image.name))
    logger.info(f"Moved {self._image.full_name} to camera's failed images")
