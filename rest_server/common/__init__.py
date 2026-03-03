import os

from common.logging import logger


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN') 
if ACCESS_TOKEN:
  logger.info('Using access token from environment variable.')
