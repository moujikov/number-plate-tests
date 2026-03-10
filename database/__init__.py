import os

from tortoise import Tortoise

from common import TZ
from common.logging import logger


DATABASE_URL = os.getenv('DATABASE_URL') 
if DATABASE_URL:
  logger.info('Using database URL from environment variable.')
else:
  raise ValueError("DATABASE_URL environment variable is not set")



async def init_database():
  await Tortoise.init(
    db_url=DATABASE_URL,
    timezone=TZ,
    modules={'models': ['database.models']}
  )

async def release_database():
  await Tortoise.close_connections()
