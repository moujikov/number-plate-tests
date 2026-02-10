from aiohttp import FormData
from common.data import DetectionDetails
from .worker import Worker


class WorkerTask:
  async def execute_on(self, worker: Worker) -> any:
    pass


class ImageDetectionWorkerTask(WorkerTask):
  def __init__(self, path: str, details: DetectionDetails):
    self._path = path
    self._filenames = []
    self._form_data = FormData()
    self._form_data.add_field("details", details)

  def add_image(self, filename: str, content_type: str, content: bytes):
    self._filenames.append(filename)
    self._form_data.add_field("images", content, 
                               filename = filename, 
                               content_type = content_type)

  async def execute_on(self, worker: Worker) -> any:
    return await worker.request("POST", self._path, self._form_data)
