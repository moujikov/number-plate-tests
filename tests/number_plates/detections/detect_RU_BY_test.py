from typing import Any
from pytest import fixture, mark

from common.types import DetectCountry
from image_processing import number_plates

  
@fixture(scope='module')
def setup():
  number_plates.setup(DetectCountry.RU, DetectCountry.BY) 



@mark.parametrize('images', ['T256HT198'])
def test_RU(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['text'] == 'T256HT198'
  assert detections[0]['region'] == 'RU'


@mark.parametrize('images', ['BY'])
def test_BY(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['text'] == '9559OE7'
  assert detections[0]['region'] == 'BY'


@mark.parametrize('images', ['EST'])
def test_unknown_country(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['region'] == 'unknown'


@mark.parametrize('images', ['T256HT198'])
def test_confidences(detections: list[dict[str, Any]]):
  confidences = detections[0]['confidences']
  assert 0.0 <= confidences['box'] <= 1.0
  assert 0.0 <= confidences['region'] <= 1.0
  assert 0.0 <= confidences['text'] <= 1.0
  assert 0.0 <= confidences['sharpness'] <= 1.0
