from enum import Enum


class DetectionDetails(str, Enum):
  FULL = "full"
  CONFIDENCE = "confidence"
  NONE = "none"
