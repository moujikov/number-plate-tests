from pytest import approx, fixture
from image_processing import detections as __detections
from common.types import DetectionDetails


@fixture
def details() -> DetectionDetails:
  return DetectionDetails.FULL

@fixture
def detections(*, 
               images: str | list[str],
               details: DetectionDetails, 
               setup):
  if isinstance(images, list):
    return __detections.detect([__asset(image) for image in images], details=details)
  return __detections.detect(__asset(images), details=details)


def __asset(name: str) -> str:
  return f'tests/detections/assets/{name}.jpg'
