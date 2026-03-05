import asyncio

from tortoise import Tortoise

from common.logging import logger
from . import CHECK_PERIOD, DATABASE_URL
from .session import SchedulerSession
from .processor import ImagesProcessor


async def init_database():
  await Tortoise.init(
    db_url=DATABASE_URL,
    modules={'models': ['processor.models.detection']}
  )
  await Tortoise.generate_schemas(safe=True)

async def main_loop(interval, periodic_function):
  await init_database()
  while True:
    # Repeat after the interval or when done, whatever comes LAST
    await asyncio.gather(
      asyncio.sleep(interval / 1000),
      periodic_function())
    
async def cleanup():
  await session.close()
  await Tortoise.close_connections()


session = SchedulerSession()
processor = ImagesProcessor(session)

try:
  asyncio.run(main_loop(CHECK_PERIOD, processor.process_new_images))
except KeyboardInterrupt:
  pass # Allows graceful exit
finally:
  asyncio.run(cleanup())
