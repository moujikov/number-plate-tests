from pytest import mark

from common.models import DetectedVehicle


@mark.parametrize('images', ['T256HT198'])
def test_car_from_back_at_daytime(detections: list[DetectedVehicle]):
  assert len(detections) == 1
  assert detections[0].type == DetectedVehicle.Type.CAR


@mark.parametrize('images', ['P100CT178-H692YP777'])
def test_two_cars_at_daytime(detections: list[DetectedVehicle]):
  assert len(detections) == 2
  assert all(d.type == DetectedVehicle.Type.CAR for d in detections)


@mark.parametrize('images', ['P641AO47'])
def test_moving_car_at_dusk(detections: list[DetectedVehicle]):
  assert len(detections) == 1
  assert detections[0].type == DetectedVehicle.Type.CAR
