import io
from aiohttp import ClientSession, ClientError, ContentTypeError, FormData

from common.types import DetectionDetails
from common.logging import logger
from . import SCHEDULER_ACCESS_TOKEN, SCHEDULER_URL


class SchedulerSession:
  def __init__(self):
    self.__client_session = None

  @property
  def _client_session(self) -> ClientSession:
    if not self.__client_session:
      headers = {}
      if SCHEDULER_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {SCHEDULER_ACCESS_TOKEN}"

      self.__client_session = ClientSession(base_url=SCHEDULER_URL, headers=headers)

    return self.__client_session
  
  async def close(self):
    if self.__client_session:
      await self.__client_session.close()
      self.__client_session = None


  async def detect(self, filename: str, contents: bytes) -> any:
    form_data = FormData()
    form_data.add_field("details", DetectionDetails.FULL)
    # Sending a large body directly with raw bytes might lock the event loop
    data_stream = io.BytesIO(contents)  # Passing io.BytesIO instead
    form_data.add_field("images", data_stream, 
                        filename = filename,
                        content_type = 'image/jpeg')

    try:
      async with self._client_session.post('detect', data=form_data) as response:
        if response.status == 200:
          return await response.json()
        else:
          try:
            data = await response.json()
          except ContentTypeError:
            data = await response.text()

          return {
            "status": response.status,
            "data": data
          }
    except ClientError as e:
      logger.debug(f'Error connecting to scheduler: {e}')
      return {
        "status": 400,
        "data": str(e)
      }
