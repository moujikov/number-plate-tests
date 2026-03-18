import asyncio
import signal
import sys

from common.logging import logger
from database import init_database, release_database
from skud.backend import Users
from . import CHECK_PERIOD
from .session import PrimeSkudWebSession
from .loader import PrimeSkudWebLoader



async def main():
  session = PrimeSkudWebSession()
  users = Users()
  processor = PrimeSkudWebLoader(session, users)

  try:
    await init_database()
    while True:   # Repeat after the interval or when done, whatever comes LAST
      await asyncio.gather(
        asyncio.sleep(CHECK_PERIOD.to_seconds()),
        processor.update_users())
  finally:
    await session.close()
    await release_database()


def shutdown(signum, frame):
  logger.info(f"Received {signal.Signals(signum).name}, shutting down.")
  sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass # Graceful exit on Ctrl+C
except SystemExit:
  pass # Graceful exit on sys.exit(0)

