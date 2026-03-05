import os
from datetime import datetime
from zoneinfo import ZoneInfo

from .. import TZ


class InputImage:
  def __init__(self, camera: str, image: os.DirEntry):
    self.camera = camera
    self.path = image.path
    self.name = image.name
    self.timestamp = datetime.fromtimestamp(
      timestamp = image.stat().st_mtime, 
      tz = ZoneInfo(TZ))

  @property
  def date_str(self) -> str:
    return self.timestamp.strftime('%Y-%m-%d')
  
  @property
  def full_name(self) -> str:
    return f'{self.camera}:{self.name}'

  def __lt__(self, other): return self.timestamp < other.timestamp
  def __le__(self, other): return self.timestamp <= other.timestamp
  def __gt__(self, other): return self.timestamp > other.timestamp
  def __ge__(self, other): return self.timestamp >= other.timestamp
  def __eq__(self, other): return self.path == other.path
  def __ne__(self, other): return self.path != other.path
  def __hash__(self): return hash(self.path)
