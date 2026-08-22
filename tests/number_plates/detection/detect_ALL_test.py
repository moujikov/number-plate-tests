from typing import Any, Callable
import cv2 as cv
from pytest import fixture, mark

from common.types import DetectCountry
from image_processing import number_plates
from common.models import ImageWithNumberPlates, DetectedNumberPlate

  
@fixture(scope='module')
def setup():
  number_plates.setup(DetectCountry.ALL)



@mark.parametrize('images', ['T256HT198'])
def test_RU(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == 'T256HT198'
  assert detections[0].region == 'RU'


@mark.parametrize('images', ['BY'])
def test_BY(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == '9559OE7'
  assert detections[0].region == 'BY'


@mark.parametrize('images', ['AM'])
def test_AM(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == '01OA090'
  assert detections[0].region == 'AM'


@mark.parametrize('images', ['GE'])
def test_GE(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == 'MA001QE'
  assert detections[0].region == 'GE'


@mark.parametrize('images', ['KG'])
def test_KG(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == '04892AAH'
  assert detections[0].region == 'KG'


@mark.parametrize('images', ['KZ'])
def test_KZ(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == '410ARZ11'
  assert detections[0].region == 'KZ'


@mark.parametrize('images', ['UA'])
def test_UA(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == 'BX5100HA'
  assert detections[0].region == 'UA'


@mark.parametrize('images', [['DE', 'EST', 'LT']], ids=['DE_EST_LT'])
def test_EU(detections: list[ImageWithNumberPlates]):
  assert len(detections) == 3
  assert {number_plate.region for image in detections for number_plate in image.number_plates} == {'EU'}
  assert {number_plates.text for number_plates in detections[0].number_plates} == {'TFS1941H'}
  assert {number_plates.text for number_plates in detections[1].number_plates} == {'396KGR'}
  assert {number_plates.text for number_plates in detections[2].number_plates} == {'EGL076'}


def test_RGB_image_detection_succeeds(asset: Callable, artifacts: Callable, setup_run, setup):
  image = cv.imread(asset('KG'), cv.IMREAD_COLOR_RGB)
  assert image is not None
  detections = number_plates.detect([image], 
                                    names=['KG-RGB'], 
                                    save_artifacts=artifacts()
                                   )[0].number_plates
  assert len(detections) == 1
  assert detections[0].region == 'KG'
  assert detections[0].text == '04892AAH'


def test_BGR_image_detection_may_fail(asset: Callable, artifacts: Callable, setup_run, setup):
  image = cv.imread(asset('KG'), cv.IMREAD_COLOR_BGR)
  assert image is not None
  detections = number_plates.detect([image], 
                                    names=['KG-BGR'], 
                                    save_artifacts=artifacts()
                                   )[0].number_plates
  assert len(detections) == 1
  assert detections[0].region != 'KG'
  assert detections[0].text != '04892AAH'
