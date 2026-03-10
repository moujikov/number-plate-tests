import asyncio

from common.logging import logger
from database import init_database, release_database
from skud.backend import Users
from . import CHECK_PERIOD
from .session import PrimeSkudWebSession
from .loader import PrimeSkudWebLoader



async def main():
  try:
    await init_database()

    session = PrimeSkudWebSession()
    users = Users()
    processor = PrimeSkudWebLoader(session, users)

    while True:   # Repeat after the interval or when done, whatever comes LAST
      await asyncio.gather(
        asyncio.sleep(CHECK_PERIOD.to_seconds()),
        processor.update_users())
  finally:
    if session: await session.close()
    await release_database()


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass # Allows graceful exit
