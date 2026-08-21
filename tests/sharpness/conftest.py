from pathlib import Path
import cv2 as cv
import os
import shutil
from pytest import approx, fixture
from image_processing import sharpness

ARTIFACTS = '.tests-artifacts/sharpness' 

@fixture(scope='package')
def setup_run():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)
  os.makedirs(ARTIFACTS)


@fixture
def assert_sharpness(category: str, number_plate: str, variant: str, 
                     method: sharpness.Method, expected: float, 
                     setup_run):
  return AssertSharpness(category, number_plate, variant, method, expected)


class AssertSharpness:
  def __init__(self, 
               category: str, number_plate: str, variant: str,
               method: sharpness.Method, expected: float):
    self._method = method
    self._category = category
    self._number_plate = number_plate
    self._variant = variant
    self._expected = expected

  def eval(self):
    path = Path('tests/sharpness/assets/') / self._category / self._number_plate / ( self._variant + '.jpg' )
    img = cv.imread(path, cv.IMREAD_COLOR_RGB)
    if img is None:
      raise FileNotFoundError(f"Image not found: {path}")

    art_dir = f'{ARTIFACTS}/{self._method.name.lower()}'
    art_file = f'{art_dir}/{self._category}-{self._number_plate}-{self._variant}.jpg'
    os.makedirs(art_dir, exist_ok=True)

    result = sharpness.measure(img, method=self._method, save_artifacts=art_file)
    assert result == approx(self._expected, abs=0.05)
