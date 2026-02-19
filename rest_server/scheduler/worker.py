from enum import Enum
from aiohttp import ClientSession, ContentTypeError, FormData


class WorkerState(str, Enum):
  FREE = "free"
  BUSY = "busy"
  CLOSED = "closed"
  # TODO: DOWN = "down"


class Worker:
  def __init__(self, id: int, url: str, access_token: str | None = None):
    self._state = WorkerState.FREE
    self._id = id
    self._url = url
    self.__access_token = access_token
    self.__client_session = None

  @property
  def _client_session(self) -> ClientSession:
    if self._state == WorkerState.CLOSED:
      raise Exception(
        f"Can't access client session for worker {self.full_str}"
        f" when it is {self._state.value}")

    if not self.__client_session:
      headers = {}
      if self.__access_token:
        headers["Authorization"] = f"Bearer {self.__access_token}"

      self.__client_session = ClientSession(base_url=self._url, headers=headers)

    return self.__client_session
  
  async def close(self):
    self._state = WorkerState.CLOSED
    if self.__client_session:
      await self.__client_session.close()
      self.__client_session = None


  async def request(self, method: str, path: str, data: FormData = None) -> any:
    if self._state != WorkerState.BUSY:
      raise Exception(f"Can't use worker {self.full_str} when it is {self._state.value}")
    
    async with self._client_session.request(method, path, data=data) as response:
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


  @property
  def is_free(self) -> bool:
    return self._state == WorkerState.FREE
  
  @property
  def is_active(self) -> bool:
    return self._state == WorkerState.FREE or self._state == WorkerState.BUSY
  
  def set_free(self):
    self._state = WorkerState.FREE

  def set_busy(self):
    self._state = WorkerState.BUSY


  @property
  def short_str(self):
    return f"#{self._id}"
    
  @property
  def full_str(self):
    return f"#{self._id} ({self._url})"
