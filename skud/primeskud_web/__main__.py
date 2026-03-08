import asyncio

from durations import Duration

from common.logging import logger
from database import init_database, release_database
from . import CHECK_PERIOD
from .session import PrimeSkudWebSession
from .loader import PrimeSkudWebLoader


async def main_loop(duration: Duration, periodic_function):
  await init_database()
  while True:
    # Repeat after the interval or when done, whatever comes LAST
    await asyncio.gather(
      asyncio.sleep(duration.to_seconds()),
      periodic_function())

async def cleanup():
  await session.close()
  await release_database()


session = PrimeSkudWebSession()
processor = PrimeSkudWebLoader(session)

try:
  asyncio.run(main_loop(CHECK_PERIOD, processor.load_new_data))
except KeyboardInterrupt:
  pass # Allows graceful exit
finally:
  asyncio.run(cleanup())
