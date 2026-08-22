from pathlib import Path
import numpy as np
from typing import Any, overload
import torch
from ultralytics import YOLO
from ultralytics.engine.results import Results

from common import utils


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



def detect(source: np.ndarray | str | Path | list[np.ndarray] | list[str] | list[Path],
           *,
           names: list[str] | None = None,
           save_artifacts: str | Path | None = None
          ) -> list[dict[str, Any]]:
  assert __model is not None
  detections = __model.predict(source,
                               conf=CONFIDENCE, iou=IOU, end2end=False, device=DEVICE,
                               save=bool(save_artifacts), save_dir=save_artifacts,
                               # Due to a bug in YOLO 'save_dir' will be cached and never updated unless 'project' or 'name' are also set:
                               name='dummy')

  results = []
  if not names: names = ['' for _ in detections]
  for image_name, image_detections in zip(names, detections, strict=True):
    assert isinstance(image_detections, Results)
    assert image_detections.boxes

    if not image_name:
      if isinstance(image_detections.orig_img, str | Path):
        image_name = Path(image_detections.orig_img).stem
      else:
        image_name = f'image_{len(results)+1}'

    image_results = []
    for cls, box, confidence in zip(
      image_detections.boxes.cls, 
      image_detections.boxes.xyxy,
      image_detections.boxes.conf):
      vehicle: str
      if cls == 2: vehicle = 'car'
      elif cls == 5: vehicle = 'bus'
      elif cls == 7: vehicle = 'truck'
      else: continue

      image_results.append({
        'vehicle': vehicle,
        'box': box.tolist(),
        'confidence': confidence.item(),
      })

    results.append({
      'image': image_name,
      'detections': image_results
    })

  return results
