from fastapi import HTTPException, status

from . import ACCESS_TOKEN
from .logging import logger


def check_authorized(access_token: str):
  if ACCESS_TOKEN:
    if access_token == ACCESS_TOKEN:
      logger.debug('Successfully authorized with ACCESS TOKEN')
    else:
      logger.warning('Authorization failed: wrong ACCESS TOKEN provided') if access_token else \
      logger.warning('Authorization failed: no ACCESS TOKEN provided')
      raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="No valid access token provided",
        headers={"WWW-Authenticate": "Bearer"})
