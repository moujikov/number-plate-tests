import asyncio

from common.logging import logger
from database import init_database, release_database
from . import CHECK_PERIOD
from .session import SchedulerSession
from .processor import ImagesProcessor



async def main():
  session = SchedulerSession()
  processor = ImagesProcessor(session)

  try:
    await init_database()
    while True:   # Repeat after the interval or when done, whatever comes LAST
      await asyncio.gather(
        asyncio.sleep(CHECK_PERIOD.to_seconds()),
        processor.process_new_images())
  finally:
    await session.close()
    await release_database()


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass # Allows graceful exit
