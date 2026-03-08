import asyncio

from common.logging import logger
from database import init_database, release_database
from . import CHECK_PERIOD
from .session import SchedulerSession
from .processor import ImagesProcessor


async def main_loop(interval, periodic_function):
  await init_database()
  while True:
    # Repeat after the interval or when done, whatever comes LAST
    await asyncio.gather(
      asyncio.sleep(interval / 1000),
      periodic_function())
    
async def cleanup():
  await session.close()
  await release_database()


session = SchedulerSession()
processor = ImagesProcessor(session)

try:
  asyncio.run(main_loop(CHECK_PERIOD, processor.process_new_images))
except KeyboardInterrupt:
  pass # Allows graceful exit
finally:
  asyncio.run(cleanup())
