import os
import shutil
from pytest import approx, fixture, FixtureRequest
from image_processing import detections as __detections
from common.types import DetectionDetails


ARTIFACTS = '.tests-artifacts/detections' 

@fixture(scope='package')
def clear_artifacts():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)
  os.makedirs(ARTIFACTS)

@fixture
def details() -> DetectionDetails:
  return DetectionDetails.FULL

@fixture
def detections(*, 
               images: str | list[str],
               details: DetectionDetails, 
               request: FixtureRequest, 
               setup, clear_artifacts):
  
  art_dir = f'{ARTIFACTS}/{request.node.parent.name.removesuffix(".py")}'
  art_file = f'{art_dir}/{request.node.originalname}.jpg'
  os.makedirs(art_dir, exist_ok=True)

  if isinstance(images, list):
    return __detections.detect(
      [__asset(image) for image in images],
      names=images,
      details=details, 
      save_artifacts=art_file)
  
  return __detections.detect(
    __asset(images),
    details=details, 
    save_artifacts=art_file)


def __asset(name: str) -> str:
  return f'tests/detections/assets/{name}.jpg'
