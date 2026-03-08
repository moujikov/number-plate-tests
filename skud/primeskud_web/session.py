from aiohttp import ClientSession, ClientError, ContentTypeError, FormData

from common.logging import logger
from . import PRIME_SKUD_URL, WEB_LOGIN, WEB_PASSWORD


class PrimeSkudWebSession:
  def __init__(self):
    self.__client_session = None

  @property
  def _client_session(self) -> ClientSession:
    if not self.__client_session:
      self.__client_session = ClientSession(base_url=PRIME_SKUD_URL)

    return self.__client_session
  
  async def close(self):
    if self.__client_session:
      await self.__client_session.close()
      self.__client_session = None


  async def login(self) -> any:
    url_params = {'unauthorized_header': '', 'user_auth': ''}
    form_data = {'auth_login': WEB_LOGIN, 'auth_passwd': WEB_PASSWORD}
    try:
      async with self._client_session.post('/', params=url_params, data=form_data) as response:
        if response.status == 200:
          logger.info(f'Successfully logged in to Prime Skud Web')
          logger.debug(f'Login response: {repr(response)}')
        else:
          logger.warning(f'Failed to log in to Prime Skud Web: {repr(response)}')
    except ClientError as e:
      logger.warning(f'Failed to log in to Prime Skud Web: {e}')
