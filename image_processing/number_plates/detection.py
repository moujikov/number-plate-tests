import asyncio
from pathlib import Path
from typing import Any, overload
import cv2 as cv
import numpy as np

from common.types import DetectCountry, DetectionDetails
from . import pipeline, sharpness



async def setup_async(*countries: DetectCountry):
  await asyncio.to_thread(setup, *countries)

def setup(*countries: DetectCountry):
  pipeline.setup(*countries)


@overload
async def detect_async(source: np.ndarray | str | Path,
                       *,
                       details: DetectionDetails = DetectionDetails.FULL,
                       save_artifacts: str | Path | None = None
                      ) -> list[dict[str, Any]]:
  """
  Async detect and decode number plates in an image.

  Args:
    source: input image path or image in RGB format.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of detected number plates
  """
  ...


@overload
async def detect_async(source: list[str] | list[Path],
                       *,
                       details: DetectionDetails = DetectionDetails.FULL,
                       save_artifacts: str | Path | None = None
                      ) -> list[dict[str, Any]]:
  """
  Async detect and decode number plates in images.

  Args:
    source: input images' paths.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of dictionaries containing detection results for each input image.
  """
  ...


@overload
async def detect_async(source: list[np.ndarray],
                       *,
                       names: list[str] | None = None,
                       details: DetectionDetails = DetectionDetails.FULL,
                       save_artifacts: str | Path | None = None
                      ) -> list[dict[str, Any]]:
  """
  Async detect and decode number plates in images.

  Args:
    source: input images in RGB format.
    names: optional image names.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of dictionaries containing detection results for each input image.
  """
  ...


async def detect_async(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
                       *,
                       names: list[str] | None = None,
                       details: DetectionDetails = DetectionDetails.FULL,
                       save_artifacts: str | Path | None = None
                      ) -> list[dict[str, Any]]:
  return await asyncio.to_thread(_detect, source, names, details, save_artifacts)


@overload
def detect(source: np.ndarray | str | Path,
           *,
           details: DetectionDetails = DetectionDetails.FULL,
           save_artifacts: str | Path | None = ...
          ) -> list[dict[str, Any]]:
  """
  Detect and decode number plates in an image.

  Args:
    source: input image path or image in RGB format.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of detected number plates.
  """
  ...


@overload
def detect(source: list[np.ndarray],
           *,
           names: list[str] | None = ...,
           details: DetectionDetails = DetectionDetails.FULL,
           save_artifacts: str | Path | None = ...
          ) -> list[dict[str, Any]]:
  """
  Detect and decode number plates in images.

  Args:
    source: input images in RGB format.
    names: optional image names.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of dictionaries containing detection results for each input image.
  """
  ...


@overload
def detect(source: list[str] | list[Path],
           *,
           details: DetectionDetails = DetectionDetails.FULL,
           save_artifacts: str | Path | None = ...
          ) -> list[dict[str, Any]]:
  """
  Detect and decode number plates in images.

  Args:
    source: input images' paths.
    details: DetectionDetails, the level of details to return.
    save_artifacts: path to a filename (.jpg) to save detection details to.

  Returns:
    a list of dictionaries containing detection results for each input image.
  """
  ...


def detect(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
           *,
           names: list[str] | None = None,
           details: DetectionDetails = DetectionDetails.FULL,
           save_artifacts: str | Path | None = None
          ) -> list[dict[str, Any]]:
  return _detect(source, names, details, save_artifacts)


def _detect(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
            names: list[str] | None,
            details: DetectionDetails,
            save_artifacts: str | Path | None
           ) -> list[dict[str, Any]]:
  if isinstance(source, list):
    return _detect_in_many(source, names, details, save_artifacts)
  return _detect_in_one(source, details, save_artifacts)


def _detect_in_one(image: np.ndarray | str | Path,
                   details: DetectionDetails,
                   save_artifacts: str | Path | None
                  ) -> list[dict[str, Any]]:
  detections = _get_detections_for_image(image)
  return _process_detections(detections, details, save_artifacts)


def _detect_in_many(images: list[np.ndarray] | list[str] | list[Path],
                    names: list[str] | None,
                    details: DetectionDetails,
                    save_artifacts: str | Path | None
                   ) -> list[dict[str, Any]]:
  if not names: names = ['' for _ in images]
  return [
    _detect_in_one_of_many(image, image_name, index, details, save_artifacts)
    for image, image_name, index
    in zip(images, names, range(len(images)), strict=True)
  ]

def _detect_in_one_of_many(image: np.ndarray | str | Path, 
                           name: str, index: int,
                           details: DetectionDetails,
                           save_artifacts: str | Path | None
                          ) -> dict[str, Any]:
  if not name:
    if isinstance(image, str | Path):
      name = Path(image).stem
    else:
      name = f'image_{index+1}'

  if save_artifacts:
      path = Path(save_artifacts)
      save_artifacts = path.parent / f'{path.stem}_{name}.jpg'

  detections = _get_detections_for_image(image)

  return {
    'image': name,
    'detections': _process_detections(detections, details, save_artifacts)
  }


def _get_detections_for_image(image: np.ndarray | str | Path) -> list:
  if isinstance(image, str | Path): 
    read_image = cv.imread(str(image), cv.IMREAD_COLOR_RGB)
    assert read_image is not None
    image = read_image

  return pipeline.call([image])[0]


def _process_detections(detections: list, 
                        details: DetectionDetails,
                        save_artifacts: str | Path | None
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

      sharpness_score = sharpness.measure(crop, save_artifacts=save_artifacts_crop)

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
