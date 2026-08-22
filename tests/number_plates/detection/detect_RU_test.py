from typing import Any
from pytest import approx, fixture, mark

from common.types import DetectCountry
from image_processing import number_plates
from common.models import ImageWithNumberPlates, DetectedNumberPlate

@fixture(scope='module')
def setup():
  number_plates.setup(DetectCountry.RU)



@mark.parametrize('images', ['no_numbers'])
def test_no_detections(detections: list[DetectedNumberPlate]):
  assert detections == []


@mark.parametrize('images', ['T256HT198'])
def test_one_detections(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == 'T256HT198'


@mark.parametrize('images', ['P100CT178-H692YP777'])
def test_two_detections(detections: list[DetectedNumberPlate]):
  assert len(detections) == 2
  assert {detection.text for detection in detections} == {'P100CT178', 'H692YP777'}


@mark.xfail
@mark.parametrize('images', ['C466KO550'])
def test_rare_region_number(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].text == 'C466KO550'


@mark.parametrize('images', ['EST'])
def test_unknown_country(detections: list[DetectedNumberPlate]):
  assert len(detections) == 1
  assert detections[0].region == 'RU'


@mark.parametrize('images', 
                  [['P641AO47-1', 'P641AO47-2', 'P641AO47-3', 'P641AO47-4']],
                  ids=['P641AO47-x'])
def test_measuring_sharpness(detections: list[ImageWithNumberPlates]):
  assert len(detections) == 4
  assert detections[0].number_plates[0].conf.sharpness == approx(0.9, abs=0.1)
  assert detections[1].number_plates[0].conf.sharpness == approx(0.7, abs=0.1)
  assert detections[2].number_plates[0].conf.sharpness == approx(0.4, abs=0.1)
  assert detections[3].number_plates[0].conf.sharpness == approx(0.2, abs=0.1)

  
  
