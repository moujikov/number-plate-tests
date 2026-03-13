from aiohttp import ClientSession, ClientError

from common.logging import logger
from . import PRIME_SKUD_URL, WEB_LOGIN, WEB_PASSWORD


class PrimeSkudWebSession:
  def __init__(self):
    self.__client_session = None
    self._logged_in = False

  @property
  def _client_session(self) -> ClientSession:
    if not self.__client_session:
      self.__client_session = ClientSession(base_url=PRIME_SKUD_URL)

    return self.__client_session
  
  async def close(self):
    if self.__client_session:
      await self.__client_session.close()
      self.__client_session = None
      self._logged_in = False

  async def login(self) -> bool:
    if self._logged_in:
      return True
    
    url_params = {'unauthorized_header': '', 'user_auth': ''}
    form_data = {'auth_login': WEB_LOGIN, 'auth_passwd': WEB_PASSWORD}
    try:
      async with self._client_session.post('/', params=url_params, data=form_data) as response:
        if response.status == 200:
          logger.info(f'Successfully logged in')
          logger.debug(f'Login response headers: {response.raw_headers}')
          self._logged_in = True
        else:
          logger.warning(f'Failed to log in, response headers: {response.raw_headers}')
          self._logged_in = False
    except ClientError as e:
      logger.warning(f'Failed to log in: {e}')
      self._logged_in = False

    return self._logged_in
  

  async def download_users_list(self) -> bytes:
    return await self.__download_users_list(is_retry=False)

  async def __download_users_list(self, is_retry: bool) -> bytes:
    if not await self.login():
      raise Exception(f"Can't log in")

    url_params = {
      'user_header': '',
      'client_export_dialog': '',
      'object_id': 790,
      'client_group_id': 1580
      }

    async with self._client_session.get('/', params=url_params) as response:
      if response.status == 200 and response.content_type == 'application/vnd.ms-excel': #OK
        response_bytes = await response.read()
        if response_bytes:
          logger.info(f'Successfully downloaded users list ({len(response_bytes)} bytes)')
          logger.debug(f'Users list response headers: {response.raw_headers}')
          return response_bytes
      
      if not is_retry:
        self._logged_in = False
        logger.warning(f'Failed to download users list. Presumably unauthorized. Retrying...')
        logger.debug(f'Users list response headers: {response.raw_headers}')
        return await self.__download_users_list(is_retry=True)

      raise Exception(f'Giving up after retry. Response headers: {response.raw_headers}')
