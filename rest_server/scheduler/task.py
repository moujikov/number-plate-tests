import io
from typing import Any
from abc import ABC, abstractmethod
from aiohttp import FormData
from .worker import Worker


class WorkerTask(ABC):
  @abstractmethod
  async def execute_on(self, worker: Worker) -> dict[str, Any]:
    pass


class ImageDetectionWorkerTask(WorkerTask):
  def __init__(self, path: str):
    self._path = path
    self._filenames = []
    self._form_data = FormData()

  def add_image(self, filename: str, content_type: str, contents: bytes):
    self._filenames.append(filename)
    # Sending a large body directly with raw bytes might lock the event loop
    data_stream = io.BytesIO(contents)  # Passing io.BytesIO instead
    self._form_data.add_field("images", data_stream, 
                               filename = filename, 
                               content_type = content_type)

  async def execute_on(self, worker: Worker) -> dict[str, Any]:
    return await worker.request("POST", self._path, self._form_data)
  
  def __str__(self):
    if len(self._filenames) == 0:
      return "(no images)"
    elif len(self._filenames) == 1:
      return self._filenames[0]
    else:
      return f"{', '.join(self._filenames)}"
