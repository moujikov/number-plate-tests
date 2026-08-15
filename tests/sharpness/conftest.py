from pathlib import Path
import cv2 as cv
import os
import shutil
from pytest import approx, fixture
from image_processing import sharpness

ARTIFACTS = '.tests-artifacts/sharpness' 

@fixture(scope='package')
def clear_artifacts():
  shutil.rmtree(ARTIFACTS, ignore_errors=True)


@fixture
def assert_sharpness(category: str, number_plate: str, variant: str, 
                     method: sharpness.Method, expected: float, 
                     clear_artifacts):
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
    img = cv.imread(path)
    if img is None:
      raise FileNotFoundError(f"Image not found: {path}")

    dir = f'{ARTIFACTS}/{self._method.name.lower()}'
    os.makedirs(dir, exist_ok=True)
    result = sharpness.measure(img, 
                               method=self._method,
                               save_artifacts=f'{dir}/{self._category}-{self._number_plate}-{self._variant}.jpg')
    assert result == approx(self._expected, abs=0.05)
