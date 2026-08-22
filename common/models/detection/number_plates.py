from enum import Enum

from torch import Tensor
  

class DetectedNumberPlate:
  class Confidences:
    def __init__(self, box: float, sharpness: float):
      self.box = box
      self.sharpness = sharpness
      self.region : float | None = None
      self.text : float | None = None

    def __repr__(self) -> str:
      str = f"Confidences: B={self.box:.2f}, S={self.sharpness:.2f}"
      if self.region is not None: str += f", R={self.region:.2f}"
      if self.text is not None: str += f", T={self.text:.2f}"
      return str

  def __init__(self, 
               region: str, 
               text: str, 
               box: list[tuple[float, float]], 
               expanded: list[tuple[float, float]],
               conf: Confidences):
    self.region = region
    self.text = text
    self.box = [(round(p[0]), round(p[1])) for p in box]
    self.expanded = [(round(p[0]), round(p[1])) for p in expanded]

    self.conf = conf

  def __repr__(self) -> str:
    str = f"Detected {self.region} number plate '{self.text}':\n"
    str += "  Box: " + ", ".join([f"({point[0]}, {point[1]})" for point in self.box]) + "\n"
    str += "  " + repr(self.conf)
    return str


class ImageWithNumberPlates:
  def __init__(self, name: str, number_plates: list[DetectedNumberPlate]):
    self.name = name
    self.number_plates = number_plates

  def __repr__(self) -> str:
    str = f"Image '{self.name}' number plates:\n"
    for number_plate in self.number_plates:
      for line in repr(number_plate).split("\n"):
        str += f"  {line}\n"
      str += "\n"
    return str
