import asyncio
from pathlib import Path
from typing import Any
import cv2 as cv
import numpy as np

from common.types import DetectCountry, DetectionDetails
from image_processing import sharpness
from . import pipeline 



async def setup_async(*countries: DetectCountry):
  await asyncio.to_thread(setup, *countries)


def setup(*countries: DetectCountry):
  pipeline.setup(*countries)


async def detect_async(images: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
                       *,
                       names: list[str] | None = None,
                       details: DetectionDetails = DetectionDetails.FULL,
                       save_artifacts: str | Path | None = None
                      ) -> list[dict[str, Any]]:
  return await asyncio.to_thread(detect, 
                                 images, 
                                 names = names, 
                                 details = details, 
                                 save_artifacts = save_artifacts)


def detect(images: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
           *,
           names: list[str] | None = None,
           details: DetectionDetails = DetectionDetails.FULL,
           save_artifacts: str | Path | None = None
          ) -> list[dict[str, Any]]:
  if isinstance(images, list):
    return _detect_in_all(images, names, details, save_artifacts)
  return _detect_in_one(images, details, save_artifacts)


def _read_image(image: np.ndarray | str | Path) -> np.ndarray:
  if isinstance(image, (str, Path)):
    read_image = cv.imread(str(image))
    assert read_image is not None
    image = read_image

  return cv.cvtColor(image, cv.COLOR_BGR2RGB)  # Underlying model expects RGB

def _read_images(images: list[np.ndarray] | list[str] | list[Path]) -> list[np.ndarray]:
  return [_read_image(image) for image in images]


def _detect_in_one(image: np.ndarray | str | Path,
                   details: DetectionDetails = DetectionDetails.FULL,
                   save_artifacts: str | Path | None = None
                  ) -> list[dict[str, Any]]:
  read_image = _read_image(image)
  detections = pipeline.call([read_image])[0]
  return _process_detections(detections, details, save_artifacts)


def _detect_in_all(images: list[np.ndarray] | list[str] | list[Path],
                   names: list[str] | None = None,
                   details: DetectionDetails = DetectionDetails.FULL,
                   save_artifacts: str | Path | None = None
                  ) -> list[dict[str, Any]]:
  read_images = _read_images(images)
  if not names: names = ['' for _ in images]

  detections = pipeline.call(read_images)
  return [
      _process_named_detections(image_name if image_name else f'image_{i+1}', 
                                image_detections,
                                details,
                                save_artifacts)
      for i, image, image_name, image_detections 
      in zip(range(len(images)), read_images, names, detections, strict=True)
    ]


def _process_named_detections(name: str,
                              detections: list[Any], 
                              details: DetectionDetails,
                              save_artifacts: str | Path | None = None
                             ) -> dict[str, Any]:
  if save_artifacts:
    path = Path(save_artifacts)
    save_artifacts = path.parent / f'{path.stem}_{name}.jpg'

  return {
    'image': name,
    'detections': _process_detections(detections, details, save_artifacts)
  }

def _process_detections(detections: list[Any], 
                        details: DetectionDetails,
                        save_artifacts: str | Path | None = None,
                       ) -> list[dict[str, Any]]:
  filtered_detections = []
  marks_image = None

  # Expected 'detections' structure: [image, [bboxes], [points], etc... , [texts]]
  # We'll skip image and iterate over detections one by one:
  for bbox, points, crop, region_id, region_name, count_line, confidence, text \
      in zip(*detections[1:], strict=True):

    filtered_detection = {}

    if details == DetectionDetails.FULL or details == DetectionDetails.CONFIDENCE:
      save_artifacts_crop = ''
      if save_artifacts:
        path = Path(save_artifacts)
        save_artifacts_crop = path.parent / f'{path.stem}_crop-{text}.jpg'

      crop_bgr = cv.cvtColor(crop, cv.COLOR_RGB2BGR)
      sharpness_score = sharpness.measure(crop_bgr, save_artifacts=save_artifacts_crop)

      confidences = {
        'box': round(float(bbox[4]), 6),
        'sharpness': round(sharpness_score, 6),
      }
      if len(pipeline.configured_countries) > 1:
        confidences['region'] = round(float(confidence[0]), 6)
        confidences['text'] = round(float(confidence[1]), 6)
      filtered_detection['confidences'] = confidences

    expanded_points = __expand(points)
    if details == DetectionDetails.FULL:
      filtered_detection['box'] = __round_points(points)
      filtered_detection['expanded_box'] = __round_points(expanded_points)

    if save_artifacts:
      if marks_image is None: 
        marks_image = cv.cvtColor(detections[0], cv.COLOR_RGB2BGR)
      __draw_polyline(marks_image, expanded_points)

    filtered_detection['region'] = region_name
    filtered_detection['text'] = text
    filtered_detections.append(filtered_detection)

  if marks_image is not None:
    cv.imwrite(str(save_artifacts), marks_image)

  return filtered_detections


def __round_points(points: list[tuple[float, float]]) -> list[tuple[int, int]]:
  return [(round(x[0]), round(x[1])) for x in points]


def __box_size(points: list[tuple[float, float]]) -> float:
  # Measure both diagonals, take the longest
  return max(( (points[0][0] - points[2][0])**2 + (points[0][1] - points[2][1])**2 ) ** 0.5,
             ( (points[1][0] - points[3][0])**2 + (points[1][1] - points[3][1])**2 ) ** 0.5)


EXPANSION_FACTOR = 0.05
def __expand(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
  gap = __box_size(points) * EXPANSION_FACTOR

  left_edge = ((points[0][0] - gap, points[0][1]), (points[1][0] - gap, points[1][1]))
  top_edge = ((points[1][0], points[1][1] - gap), (points[2][0], points[2][1] - gap))
  right_edge = ((points[2][0] + gap, points[2][1]), (points[3][0] + gap, points[3][1]))
  bottom_edge = ((points[3][0], points[3][1] + gap), (points[0][0], points[0][1] + gap))

  top_left = __intersection_point(top_edge, left_edge)
  top_right = __intersection_point(top_edge, right_edge)
  bottom_right = __intersection_point(bottom_edge, right_edge)
  bottom_left = __intersection_point(bottom_edge, left_edge)

  return [bottom_left, top_left, top_right, bottom_right]


def __intersection_point(line1: tuple[tuple[float, float], tuple[float, float]], 
                         line2: tuple[tuple[float, float], tuple[float, float]]
                        ) -> tuple[float, float]:
  xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
  ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

  def det(a, b):
    return a[0] * b[1] - a[1] * b[0]

  div = det(xdiff, ydiff)
  if div == 0:
    raise ValueError("lines do not intersect")

  d = (det(line1[0], line1[1]), det(line2[0], line2[1]))
  x = det(d, xdiff) / div
  y = det(d, ydiff) / div
  return x, y


LINE_COLOR = (0, 255, 0)
LINE_THICKNESS_FACTOR = 0.02
MIN_LINE_THICKNESS = 2
def __draw_polyline(image: np.ndarray, points: list[tuple[float, float]]):
  thickness = max(round(__box_size(points) * LINE_THICKNESS_FACTOR), MIN_LINE_THICKNESS)
  cv.polylines(image, 
               [np.array(points, dtype=np.int32)], 
               isClosed=True, color=LINE_COLOR, 
               thickness=thickness)
