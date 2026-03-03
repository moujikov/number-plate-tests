from datetime import datetime
import os


class InputImage:
  def __init__(self, camera: str, image: os.DirEntry):
    self.camera = camera
    self.path = image.path
    self.name = image.name
    self._timestamp = datetime.fromtimestamp(image.stat().st_mtime)

  @property
  def date_str(self) -> str:
    return self._timestamp.strftime('%Y-%m-%d')
  
  @property
  def full_name(self) -> str:
    return f'{self.camera}:{self.name}'

  def __lt__(self, other): return self._timestamp < other._timestamp
  def __le__(self, other): return self._timestamp <= other._timestamp
  def __gt__(self, other): return self._timestamp > other._timestamp
  def __ge__(self, other): return self._timestamp >= other._timestamp
  def __eq__(self, other): return self.path == other.path
  def __ne__(self, other): return self.path != other.path
  def __hash__(self): return hash(self.path)
