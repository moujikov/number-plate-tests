import os

from fastapi import HTTPException, status

from common.logging import logger


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN') 
if ACCESS_TOKEN:
  logger.info('Using access token from environment variable.')


def check_authorized(access_token: str):
  if ACCESS_TOKEN and access_token != ACCESS_TOKEN:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
