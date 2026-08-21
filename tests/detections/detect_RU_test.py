from typing import Any
from pytest import approx, fixture, mark

from common.types import DetectionDetails
from image_processing import detections as __detections
  
@fixture(scope='module')
def setup():
  __detections.setup(__detections.DetectCountry.RU)



@mark.parametrize('images', ['T256HT198'])
def test_detection_structure(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  detection = detections[0]

  assert isinstance(detection, dict)
  assert set(detection.keys()) == {'text', 'region', 'box', 'expanded_box', 'confidences'}
  
  assert isinstance(detection['text'], str)
  assert isinstance(detection['region'], str)
  assert isinstance(detection['box'], list)
  assert len(detection['box']) == 4
  assert isinstance(detection['confidences'], dict)


@mark.parametrize(['images', 'details'], [('T256HT198', DetectionDetails.NONE)])
def test_detection_with_no_details(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert set(detections[0].keys()) == {'text', 'region'}


@mark.parametrize(['images', 'details'], [('T256HT198', DetectionDetails.CONFIDENCE)])
def test_detection_with_confidence_details(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert set(detections[0].keys()) == {'text', 'region', 'confidences'}


@mark.parametrize('images', ['no_numbers'])
def test_no_detections(detections: list[dict[str, Any]]):
  assert detections == []


@mark.parametrize('images', ['T256HT198'])
def test_one_detections(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['text'] == 'T256HT198'


@mark.parametrize('images', ['P100CT178-H692YP777'])
def test_two_detections(detections: list[dict[str, Any]]):
  assert len(detections) == 2
  assert {detection['text'] for detection in detections} == {'P100CT178', 'H692YP777'}


@mark.xfail
@mark.parametrize('images', ['C466KO550'])
def test_rare_region_number(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['text'] == 'C466KO550'


@mark.parametrize('images', ['EST'])
def test_unknown_country(detections: list[dict[str, Any]]):
  assert len(detections) == 1
  assert detections[0]['region'] == 'RU'


@mark.parametrize('images', 
                  [['P641AO47-1', 'P641AO47-2', 'P641AO47-3', 'P641AO47-4']],
                  ids=['P641AO47-x'])
def test_measuring_sharpness(detections: list[dict[str, Any]]):
  assert len(detections) == 4
  assert detections[0]['detections'][0]['confidences']['sharpness'] == approx(0.9, abs=0.1)
  assert detections[1]['detections'][0]['confidences']['sharpness'] == approx(0.7, abs=0.1)
  assert detections[2]['detections'][0]['confidences']['sharpness'] == approx(0.4, abs=0.1)
  assert detections[3]['detections'][0]['confidences']['sharpness'] == approx(0.2, abs=0.1)

  
  
