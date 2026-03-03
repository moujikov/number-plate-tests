from fastapi import HTTPException, status

from . import ACCESS_TOKEN


def check_authorized(access_token: str):
  if ACCESS_TOKEN and access_token != ACCESS_TOKEN:
    raise HTTPException(
      status.HTTP_401_UNAUTHORIZED,
      detail="No valid access token provided",
      headers={"WWW-Authenticate": "Bearer"})
