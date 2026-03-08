from enum import Enum


class DetectionDetails(str, Enum):
  FULL = "full"
  CONFIDENCE = "confidence"
  NONE = "none"


class DetectCountry(str, Enum):
  ALL = "ALL"
  RU = "RU"; BY = "BY"; AM = "AM"; GE = "GE"; KZ = "KZ"; KG = "KG"; UA = "UA"; EU = "EU"
