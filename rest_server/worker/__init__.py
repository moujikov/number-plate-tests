import os

from common.logging import logger


HOST = os.getenv('BIND', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
logger.info(f'Listening on {HOST}:{PORT}')

MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 0))
if MAX_CONCURRENT_REQUESTS > 0:
  logger.info(f'Setting max concurrent requests to {MAX_CONCURRENT_REQUESTS}.')


DETECT_COUNTRIES = os.getenv('DETECT_COUNTRIES', 'RU')
logger.info(f'Detecting number plate types: {DETECT_COUNTRIES}')
