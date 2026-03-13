import asyncio

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


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass # Allows graceful exit
