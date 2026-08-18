import asyncio
from pathlib import Path
from typing import Any
from numpy import ndarray
from collections.abc import Collection

from common.types import DetectCountry, DetectionDetails
from image_processing import jpeg, sharpness
from . import pipeline 



async def setup_async(*countries: DetectCountry):
  await asyncio.to_thread(setup, *countries)


def setup(*countries: DetectCountry):
  pipeline.setup(*countries)


async def detect_async(images: ndarray | str | Path | list[ndarray|str|Path],
                       *,
                       names: list[str] | None = None,
                       details: DetectionDetails = DetectionDetails.FULL
                      ) -> list[dict[str, Any]]:
  return await asyncio.to_thread(detect, images, names = names, details = details)


def detect(images: ndarray | str | Path | list[ndarray|str|Path],
           *,
           names: list[str] | None = None,
           details: DetectionDetails = DetectionDetails.FULL
          ) -> list[dict[str, Any]]:
  if isinstance(images, list):
    return _detect_in_all(images, names, details)
  return _detect_in_one(images, details)


def _read_image(image: ndarray | str | Path) -> ndarray:
  if isinstance(image, ndarray):
    return image
  return jpeg.read_local_image(str(image))

def _read_images(images: list[ndarray|str|Path]) -> list[ndarray]:
  return [_read_image(image) for image in images]


def _detect_in_one(image: ndarray | str | Path,
                   details: DetectionDetails = DetectionDetails.FULL
                  ) -> list[dict[str, Any]]:
  read_image = _read_image(image)
  detections = pipeline.call([read_image])
  return _filter_image_detections(detections[0], details)


def _detect_in_all(images: list[ndarray|str|Path],
                   names: list[str] | None = None,
                   details: DetectionDetails = DetectionDetails.FULL
                  ) -> list[dict[str, Any]]:
  read_images = _read_images(images)
  if not names: names = ['' for _ in images]

  detections = pipeline.call(read_images)
  return [
      {
        'image': image_name if image_name else f'image_{i+1}',
        'detections': _filter_image_detections(image_detections, details)
      }
      for i, image_name, image_detections 
      in zip(range(len(images)), names, detections, strict=True)
    ]


def _filter_image_detections(detections: list[Any], 
                             details: DetectionDetails
                            ) -> list[dict[str, Any]]:
  filtered_detections = []

  # Expected 'detections' structure: [image, [bboxes], [points], etc... , [texts]]
  # We'll skip image and iterate over detections one by one:
  for bbox, points, crop, region_id, region_name, count_line, confidence, text \
      in zip(*detections[1:], strict=True):

    filtered_detection = {}

    if details == DetectionDetails.FULL or details == DetectionDetails.CONFIDENCE:
      confidences = {
        'box': round(float(bbox[4]), 6),
        'sharpness': round(sharpness.measure(crop), 6),
      }
      if len(pipeline.configured_countries) > 1:
        confidences['region'] = round(float(confidence[0]), 6)
        confidences['text'] = round(float(confidence[1]), 6)
      filtered_detection['confidences'] = confidences

    if details == DetectionDetails.FULL:
      filtered_detection['box'] = __int_points(points)

    filtered_detection['region'] = region_name
    filtered_detection['text'] = text
    filtered_detections.append(filtered_detection)

  return filtered_detections


def __int_points(points: Collection | float):
  if isinstance(points, Collection):
    return [__int_points(x) for x in points]
  
  return round(points)
