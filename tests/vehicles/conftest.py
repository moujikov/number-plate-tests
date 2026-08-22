import os
import shutil
from typing import Callable
from pytest import fixture, FixtureRequest
from common.models import ImageWithVehicles, Vehicle
from image_processing import vehicles


ASSETS = 'tests/vehicles/assets'
ARTIFACTS = '.tests-artifacts/vehicles'

@fixture(scope='package')
def setup_run():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)
  os.makedirs(ARTIFACTS)
  vehicles.setup()

@fixture
def asset():
  def __asset(name: str) -> str:
    return f'{ASSETS}/{name}.jpg'
  return __asset


@fixture
def detections(*, 
               images: str | list[str],
               asset: Callable[[str], str],
               setup_run) -> list[ImageWithVehicles] | list[Vehicle]:

  if isinstance(images, list):
    return vehicles.detect(
      [asset(image) for image in images],
      save_artifacts=ARTIFACTS)
  
  return vehicles.detect(asset(images), save_artifacts=ARTIFACTS)
