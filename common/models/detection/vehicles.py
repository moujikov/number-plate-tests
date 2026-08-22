from enum import Enum

from torch import Tensor
  

class DetectedVehicle:
  class Type(Enum):
    CAR = 2
    BUS = 5
    TRUCK = 7

  def __init__(self, type: Tensor, box: Tensor, conf: Tensor):
    self.type = self.Type(int(type))
    self.box = [round(float(t)) for t in box]
    self.conf = float(conf)

  def __repr__(self) -> str:
    return (f"{self.type.name}: "
            f"({self.box[0]}, {self.box[1]}), ({self.box[2]}, {self.box[3]}); "
            f"conf={self.conf:.2f}")


class ImageWithVehicles:
  def __init__(self, name: str, vehicles: list[DetectedVehicle]):
    self.name = name
    self.vehicles = vehicles

  def __repr__(self) -> str:
    return (f"Image '{self.name}' vehicles: \n" +
             "\n".join([f"  {v}" for v in self.vehicles]) +
             "\n")
