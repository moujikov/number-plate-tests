import asyncio

from common.logging import logger
from database import init_database, release_database
from . import CHECK_PERIOD
from .session import SchedulerSession
from .processor import ImagesProcessor



async def main():
  try:
    await init_database()

    session = SchedulerSession()
    processor = ImagesProcessor(session)

    while True:   # Repeat after the interval or when done, whatever comes LAST
      await asyncio.gather(
        asyncio.sleep(CHECK_PERIOD / 1000),
        processor.process_new_images())
  finally:
    if session: await session.close()
    await release_database()


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass # Allows graceful exit
