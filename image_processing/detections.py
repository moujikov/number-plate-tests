import asyncio
from typing import Any
from numpy import ndarray
from collections.abc import Collection

from common.types import DetectCountry, DetectionDetails
from . import pipeline 



async def setup_async(*countries: DetectCountry):
  await asyncio.to_thread(setup, *countries)


def setup(*countries: DetectCountry):
  pipeline.setup(*countries)


async def detect_async(images: list[ndarray] | ndarray,
                       *,
                       names: list[str] | None = None,
                       details: DetectionDetails = DetectionDetails.FULL
                      ) -> list[dict[str, Any]]:
  return await asyncio.to_thread(detect, images, names = names, details = details)


def detect(images: list[ndarray] | ndarray,
           *,
           names: list[str] | None = None,
           details: DetectionDetails = DetectionDetails.FULL
          ) -> list[dict[str, Any]]:
  if isinstance(images, ndarray):
    detections = pipeline.call([images])
    return _filter_image_detections(detections[0], details)

  if not names: names = ['' for _ in images]

  detections = pipeline.call(images)
  return [
      {
        "image": image_name if image_name else f'image_{i+1}',
        "detections": _filter_image_detections(image_detections, details)
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
      confidences = {"box": round(float(bbox[4]), 6)}
      if len(pipeline.configured_countries) > 1:
        confidences["region"] = round(float(confidence[0]), 6)
      confidences["text"] = round(float(confidence[1]), 6)
      filtered_detection["confidences"] = confidences

    if details == DetectionDetails.FULL:
      filtered_detection["box"] = __int_points(points)

    filtered_detection["region"] = region_name
    filtered_detection["text"] = text
    filtered_detections.append(filtered_detection)

  return filtered_detections


def __int_points(points: Collection | float):
  if isinstance(points, Collection):
    return [__int_points(x) for x in points]
  
  return round(points)
