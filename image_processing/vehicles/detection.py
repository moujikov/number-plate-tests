import asyncio
from pathlib import Path
import numpy as np
from typing import Any, overload
import torch
from ultralytics import YOLO
from ultralytics.engine.results import Results

from common import utils
from common.models import ImageWithVehicles, Vehicle, VehicleType


CONFIDENCE = 0.5
IOU = 0.7
DEVICE = None
__model: YOLO | None = None


def setup():
  global __model, DEVICE

  utils.make_gitignored_dir('.weights')
  __model = YOLO(f'.weights/yolo26x.pt')

  if torch.cuda.is_available():
    DEVICE = 'cuda'
  elif torch.mps.is_available():
    DEVICE = 'mps'
  else:
    DEVICE = 'cpu'

@overload
async def detect_async(source: np.ndarray | str | Path,
                 *,
                 save_artifacts: str | Path | None = None
                ) -> list[Vehicle]:
  ...

@overload
async def detect_async(source: list[np.ndarray],
                 *,
                 names: list[str] | None = None,
                 save_artifacts: str | Path | None = None,
                ) -> list[ImageWithVehicles]:
  ...

@overload
async def detect_async(source: list[str] | list[Path],
                 *,
                 save_artifacts: str | Path | None = None,
                ) -> list[ImageWithVehicles]:
  ...

async def detect_async(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
                       *,
                       names: list[str] | None = None,
                       save_artifacts: str | Path | None = None
                      ) -> list[ImageWithVehicles] | list[Vehicle]:
  return await asyncio.to_thread(_detect, source, names, save_artifacts)


@overload
def detect(source: np.ndarray | str | Path,
           *,
           save_artifacts: str | Path | None = None
          ) -> list[Vehicle]:
  ...

@overload
def detect(source: list[np.ndarray],
           *,
           names: list[str] | None = None,
           save_artifacts: str | Path | None = None,
          ) -> list[ImageWithVehicles]:
  ...

@overload
def detect(source: list[str] | list[Path],
           *,
           save_artifacts: str | Path | None = None,
          ) -> list[ImageWithVehicles]:
  ...

def detect(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
           *,
           names: list[str] | None = None,
           save_artifacts: str | Path | None = None
          ) -> list[ImageWithVehicles] | list[Vehicle]:
  return _detect(source, names, save_artifacts)


def _detect(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
            names: list[str] | None,
            save_artifacts: str | Path | None
           ) -> list[ImageWithVehicles] | list[Vehicle]:
  assert __model is not None
  detections = __model.predict(source,
                               conf=CONFIDENCE, iou=IOU, end2end=True, device=DEVICE,
                               # Detect only known vehicle types:
                               classes=[v.value for v in VehicleType],
                               # Treat all vehicle types equally during NMS, i.e. if we detect car and bus with almost matching boxes – take only one of them:
                               agnostic_nms=True,
                               save=bool(save_artifacts), save_dir=save_artifacts,
                               # Due to a bug in YOLO 'save_dir' will be cached and never updated unless 'project' or 'name' are also set:
                               name='dummy')
  if not isinstance(source, list) and len(list(detections)) == 1:
    return detected_vehicles(list(detections)[0])

  if not names:
    if isinstance(source, list):
      names = [Path(src).stem if isinstance(src, str | Path) else f'image_{i+1}' 
               for i, src in enumerate(source)]
    else:
      names = [f'image_{i+1}' for i, _ in enumerate(detections)]

  return [
    ImageWithVehicles(image_name, detected_vehicles(image_detections))
    for image_name, image_detections
    in zip(names, detections, strict=True)
  ]


def detected_vehicles(results: Any) -> list[Vehicle]:
  assert isinstance(results, Results)
  if not results.boxes: return []
  return [
    Vehicle(cls, box, confidence)
    for cls, box, confidence 
    in zip(results.boxes.cls, 
           results.boxes.xyxy, 
           results.boxes.conf)
  ]
