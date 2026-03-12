import os

from common.logging import logger


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN') 
if ACCESS_TOKEN:
  logger.info('Using access token from environment variable')
else:
  ACCESS_TOKEN_PATH = os.getenv('ACCESS_TOKEN_PATH')
  if ACCESS_TOKEN_PATH:
    try:
      with open(ACCESS_TOKEN_PATH) as f:
        ACCESS_TOKEN = f.read().strip()
        logger.info('Using access token from secret')
    except FileNotFoundError:
      raise ValueError(f"No access token secret found at ACCESS_TOKEN_PATH value '{ACCESS_TOKEN_PATH}'")
  else:
    raise ValueError('No access token provided in ACCESS_TOKEN / ACCESS_TOKEN_PATH environment variables')
