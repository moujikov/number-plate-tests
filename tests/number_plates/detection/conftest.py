import os
import shutil
from typing import Any, Callable
from pytest import fixture, FixtureRequest
from image_processing import number_plates
from common.models import ImageWithNumberPlates, DetectedNumberPlate


ASSETS = 'tests/number_plates/detection/assets'
ARTIFACTS = '.tests-artifacts/number_plates/detection'

@fixture(scope='package')
def setup_run():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)

@fixture
def asset():
  def __asset(name: str) -> str:
    return f'{ASSETS}/{name}.jpg'
  return __asset

@fixture
def artifacts(request: FixtureRequest):
  def __artifacts() -> str:
    return f'{ARTIFACTS}/{request.node.parent.name.removesuffix(".py")}'

  return __artifacts


@fixture
def detections(*, 
               images: str | list[str],
               asset: Callable[[str], str],
               artifacts: Callable[[], str],
               setup_run, setup) -> list[ImageWithNumberPlates] | list[DetectedNumberPlate]:

  if isinstance(images, list):
    return number_plates.detect(
      [asset(image) for image in images],
      save_artifacts=artifacts())
  
  return number_plates.detect(
    asset(images),
    save_artifacts=artifacts())
