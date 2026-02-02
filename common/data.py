from enum import Enum


class DetectionDetails(str, Enum):
  FULL = "full"
  REGION = "region"
  NONE = "none"
