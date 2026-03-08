from common.logging import logger
from .session import PrimeSkudWebSession


class PrimeSkudWebLoader:
  def __init__(self, session: PrimeSkudWebSession):
    self._session = session

  async def load_new_data(self):
    pass
