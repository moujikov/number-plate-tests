import os

from tortoise import Tortoise

from common import TZ
from common.logging import logger


DATABASE_TYPE = os.getenv('DATABASE_TYPE')
if not DATABASE_TYPE:
  raise ValueError('DATABASE_TYPE environment variable is not set')

DATABASE_HOST = os.getenv('DATABASE_HOST')
if not DATABASE_HOST:
  raise ValueError('DATABASE_HOST environment variable is not set')

DATABASE_PORT = os.getenv('DATABASE_PORT')
if not DATABASE_PORT:
  raise ValueError('DATABASE_PORT environment variable is not set')

DATABASE_NAME = os.getenv('DATABASE_NAME') 
if not DATABASE_NAME:
  raise ValueError('DATABASE_NAME environment variable is not set')

logger.info(f"Using database '{DATABASE_TYPE}://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'")
              
DATABASE_USER = os.getenv('DATABASE_USER') 
if not DATABASE_USER:
  raise ValueError('DATABASE_USER environment variable is not set')

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
if DATABASE_PASSWORD:
  logger.info(f"Accessing database as user '{DATABASE_USER}' with password from environment variable")
else:
  try:
    with open(f'/run/secrets/db_password_{DATABASE_USER}') as f:
      DATABASE_PASSWORD = f.read().strip()
      logger.info(f"Accessing database as user '{DATABASE_USER}' with password from secret")
  except FileNotFoundError:
    raise ValueError(
      f"No database password secret found for user '{DATABASE_USER}'"
      f" and DATABASE_PASSWORD environment variable is not set")


database_url=f'{DATABASE_TYPE}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

async def init_database():
  await Tortoise.init(
    db_url=database_url,
    timezone=TZ,
    modules={'models': ['database.models']}
  )

async def release_database():
  await Tortoise.close_connections()
