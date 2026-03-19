import asyncio
import signal
import sys
from typing import Callable
from durations import Duration

from common.logging import logger
from database import init_database, release_database
from skud.backend import Access, Users
from . import USERS_CHECK_PERIOD, ACCESS_CHECK_PERIOD
from .session import PrimeSkudWebSession
from .loader import PrimeSkudWebLoader


async def main():
  session = PrimeSkudWebSession()
  access = Access()
  users = Users()
  processor = PrimeSkudWebLoader(session, access, users)

  try:
    await init_database()
    await asyncio.gather(      
      __periodically_do(USERS_CHECK_PERIOD, processor.update_users),
      __periodically_do(ACCESS_CHECK_PERIOD, processor.update_access_events),
    )
  finally:
    await session.close()
    await release_database()


async def __periodically_do(interval: Duration, task: Callable, *args, **kwargs):
  while True:   # Repeat after the interval or when done, whatever comes LAST
    await asyncio.gather(
      asyncio.sleep(interval.to_seconds()),
      task(*args, **kwargs))


signal.signal(signal.SIGTERM, lambda _1, _2: sys.exit(0))

try:
  asyncio.run(main())
except KeyboardInterrupt:   # Graceful exit on Ctrl+C
  logger.info("Received SIGINT (Ctrl+C), shutting down.")
except SystemExit:          # Graceful exit on sys.exit(0)
  logger.info(f"Received SIGTERM, shutting down.")

