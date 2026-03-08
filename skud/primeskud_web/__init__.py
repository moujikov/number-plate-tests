import os

from durations import Duration
from common.logging import logger


CHECK_PERIOD = Duration(os.getenv('CHECK_PERIOD', '1h'))
logger.info(f'Checking for new images every {CHECK_PERIOD.representation}')

PRIME_SKUD_URL = os.getenv('PRIME_SKUD_URL')
if PRIME_SKUD_URL:
  logger.info(f'Using Prime Skud URL: {PRIME_SKUD_URL}')
else:
  raise ValueError("PRIME_SKUD_URL environment variable is not set")

WEB_LOGIN = os.getenv('WEB_LOGIN')
if WEB_LOGIN:
  logger.info(f'Logging into web interface as {WEB_LOGIN}')
else:
  raise ValueError("WEB_LOGIN environment variable is not set")

WEB_PASSWORD = os.getenv('WEB_PASSWORD')
if WEB_PASSWORD is not None:
  logger.info(f'Using web password from environment variable')
else:
  try:
    with open('/run/secrets/web_password') as f:
      WEB_PASSWORD = f.read().strip()
      logger.info(f'Using web password from secret')
  except FileNotFoundError:
    raise ValueError("No web_password secret found and WEB_PASSWORD environment variable is not set")
