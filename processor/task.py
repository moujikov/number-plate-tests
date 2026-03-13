import os
import re
import uuid
from datetime import timedelta

import aiofiles
import aioshutil
from aiofiles import os as aio_os

from common.types import DetectCountry
from common.logging import logger
from database.models import Detection

from . import CAMERAS_DIR, IGNORE_PERIOD, IMAGES_DIR
from .image import InputImage
from .session import SchedulerSession



class Task:
  async def fullfill(self):
    pass

class DetectionTask(Task):
  def __init__(self, session: SchedulerSession, image: InputImage):
    self._session = session
    self._image = image
    self.__processed_file_name = None

  @property
  def _processed_file_dir(self):
    return self._image.date_str

  @property
  def _processed_file_name(self):
    if not self.__processed_file_name:
      self.__processed_file_name = os.path.join(self._processed_file_dir, f'{uuid.uuid4()}.jpg')

    return self.__processed_file_name
  

  async def fullfill(self):
    async with aiofiles.open(self._image.path, mode='rb') as file:
      contents = await file.read()

    results = await self._session.detect(f'{self._image.full_name}', contents)
    logger.debug(f'Image {self._image.full_name} detection results: {results}')

    try:
      detections = self.__extract_detections(results)
    except ValueError as e:
      logger.warning(f'Image {self._image.full_name} invalid results: {e}')
      await self.__move_to_failed()
      return

    if not detections:
      await self.__delete()
      return

    saved, invalid, repeated = [], [], []
    recent = await self.__fetch_recent_detections()

    for detection in detections:
      if 'text' not in detection or 'region' not in detection:
        logger.warning(f'Image {self._image.full_name} text/region missing in detection: {results}')
        continue

      text = str(detection['text'])
      region = str(detection['region'])
      box = str(detection['box']) if 'box' in detection else None

      if text in recent:
        repeated.append(text)
        continue

      if not self.__check_valid(region, text):
        invalid.append(text)
        continue

      await self.__save_detection(text, region, box)
      saved.append(text)

    if saved: logger.info(f'Detections saved: {", ".join(saved)} ({self._image.full_name})')
    if invalid: logger.info(f'Detections ignored: {", ".join(invalid)} ({self._image.full_name})')
    if repeated: logger.info(f'Detections repeated: {", ".join(repeated)} ({self._image.full_name})')

    if saved:
      await self.__move_to_processed()
    else:
      await self.__delete()


  async def __save_detection(self, number_plate: str, region: str, box: str | None = None):
    detection = Detection(
      timestamp = self._image.timestamp,
      number_plate = number_plate,
      region = region,
      box = box,
      camera = self._image.camera,
      image = self._processed_file_name
      )
    await detection.save()


  async def __fetch_recent_detections(self) -> set[str]:
    filter = Detection.filter(timestamp__gte = self._image.timestamp - timedelta(seconds=IGNORE_PERIOD))
    return set([number_plate[0] for number_plate in await filter.values_list('number_plate')])


  __RU_LETTERS = 'ABEKMHOPCTYX'
  __RU_PATTERN = re.compile(rf'[{__RU_LETTERS}]\d{{3}}[{__RU_LETTERS}]{{2}}\d{{2,3}}')

  def __check_valid(self, region: str, text: str) -> bool:
    if region == DetectCountry.RU.value:
      if re.fullmatch(self.__RU_PATTERN, text): return True
      
    return False


  def __extract_detections(self, results: dict) -> list[dict] | None:
    if 'images' not in results: 
      raise ValueError(f'Missing "images" field: {results}')
    results = results['images']
    if not isinstance(results, list) or len(results) != 1: 
      raise ValueError(f'Invalid "images" field: {results}')
    results = results[0]
    if 'detections' not in results:
      raise ValueError(f'Missing "detections" field: {results}')
    detections = results['detections']
    if not isinstance(detections, list):
      raise ValueError(f'Invalid "detections" field: {results}')

    return detections


  async def __move_to_processed(self):
    await aio_os.makedirs(os.path.join(IMAGES_DIR, self._processed_file_dir), exist_ok=True)
    await aioshutil.move(self._image.path, os.path.join(IMAGES_DIR, self._processed_file_name))
    logger.info(f'Saved {self._image.full_name} to {self._processed_file_name}')


  async def __move_to_failed(self):
    failed_dir = os.path.join(CAMERAS_DIR, self._image.camera, 'failed')
    await aio_os.makedirs(failed_dir, exist_ok=True)
    await aioshutil.move(self._image.path, os.path.join(failed_dir, self._image.name))
    logger.warning(f"Moved {self._image.full_name} to camera's failed images")


  async def __delete(self):
    await aio_os.remove(self._image.path)
    logger.debug(f"No detections to keep, deleted {self._image.full_name}")
