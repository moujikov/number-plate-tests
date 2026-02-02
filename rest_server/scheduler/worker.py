from typing import List
from fastapi import UploadFile

from common.data import DetectionDetails


class Worker:
  url: str
  access_token: str | None

  def __init__(self, url: str, access_token: str | None = None):
    self.url = url
    self.access_token = access_token
    
  def forward(self, path: str, files: List[UploadFile], details: DetectionDetails):
    pass  # Implementation of forwarding request to worker
