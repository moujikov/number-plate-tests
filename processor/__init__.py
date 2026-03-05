import os

from common.logging import logger

TZ = os.getenv('TZ', 'UTC')
logger.info(f'Using timezone {TZ}')

CHECK_PERIOD = int(os.getenv('CHECK_PERIOD', 100))
logger.info(f'Checking for new images every {CHECK_PERIOD}ms')

PROCESS_AT_ONCE = int(os.getenv('PROCESS_AT_ONCE', 20))
logger.info(f'Processing at most {PROCESS_AT_ONCE} images at once')

CAMERAS_DIR = os.getenv('CAMERAS_DIR')
if CAMERAS_DIR:
  logger.info(f'Watching for new images in {CAMERAS_DIR}')
  cameras = sorted(os.listdir(CAMERAS_DIR))
  logger.debug(f'Found cameras: {cameras}')
  for camera in cameras:
    upload = os.path.join(CAMERAS_DIR, camera, 'upload')
    if not os.path.isdir(upload):
      logger.debug(f'WARNING: No uploads directory for camera {camera}')
else:
  raise ValueError("CAMERAS_DIR environment variable is not set")


IMAGES_DIR = os.getenv('IMAGES_DIR')
if IMAGES_DIR:
  logger.info(f'Saving processed images to {IMAGES_DIR}')
else:
  raise ValueError("IMAGES_DIR environment variable is not set")

SCHEDULER_URL = os.getenv('SCHEDULER_URL') 
if SCHEDULER_URL:
  logger.info(f'Using scheduler at {SCHEDULER_URL}')
else:
  raise ValueError("SCHEDULER_URL environment variable is not set")

SCHEDULER_ACCESS_TOKEN = os.getenv('SCHEDULER_ACCESS_TOKEN') 
if SCHEDULER_ACCESS_TOKEN:
  logger.info('Using scheduler access token from environment variable.')


DATABASE_URL = os.getenv('DATABASE_URL') 
if DATABASE_URL:
  logger.info('Using database URL from environment variable.')
else:
  raise ValueError("DATABASE_URL environment variable is not set")
