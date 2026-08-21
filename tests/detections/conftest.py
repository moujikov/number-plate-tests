import os
import shutil
from typing import Callable
from pytest import approx, fixture, FixtureRequest
from image_processing import detections as __detections
from common.types import DetectionDetails


ASSETS = 'tests/detections/assets'
ARTIFACTS = '.tests-artifacts/detections' 

@fixture(scope='package')
def setup_run():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)
  os.makedirs(ARTIFACTS)

@fixture
def asset():
  def __asset(name: str) -> str:
    return f'{ASSETS}/{name}.jpg'
  return __asset

@fixture
def artifact(request: FixtureRequest):
  def __artifact() -> str:
    art_dir = f'{ARTIFACTS}/{request.node.parent.name.removesuffix(".py")}'
    os.makedirs(art_dir, exist_ok=True)
    return f'{art_dir}/{request.node.originalname}.jpg'

  return __artifact


@fixture
def details() -> DetectionDetails:
  return DetectionDetails.FULL

@fixture
def detections(*, 
               images: str | list[str],
               details: DetectionDetails,
               asset: Callable[[str], str],
               artifact: Callable[[], str],
               setup_run, setup):

  if isinstance(images, list):
    return __detections.detect(
      [asset(image) for image in images],
      names=images,
      details=details, 
      save_artifacts=artifact())
  
  return __detections.detect(
    asset(images),
    details=details, 
    save_artifacts=artifact())
