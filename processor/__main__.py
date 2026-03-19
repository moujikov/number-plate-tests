import asyncio
import signal
import sys

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


signal.signal(signal.SIGTERM, lambda _1, _2: sys.exit(0))

try:
  asyncio.run(main())
except KeyboardInterrupt:   # Graceful exit on Ctrl+C
  logger.info("Received SIGINT (Ctrl+C), shutting down.")
except SystemExit:          # Graceful exit on sys.exit(0)
  logger.info(f"Received SIGTERM, shutting down.")
