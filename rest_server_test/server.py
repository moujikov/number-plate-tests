import sys
import traceback
import time
import logging
from fastapi import FastAPI, File, Form, Request, UploadFile,  status
from fastapi.responses import ORJSONResponse as JSONResponse
from starlette_prometheus import PrometheusMiddleware
from starlette_prometheus import metrics
from typing import List
from enum import Enum

from test_images import all_test_image_paths
from utils.jpeg import read_image
from utils.pipelines import full_pipeline, ru_pipeline


class DetectionDetails(str, Enum):
  FULL = "full"
  REGION = "region"
  NONE = "none"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000)
    logger.info(f"Completed in {process_time}ms with status {response.status_code}")
    return response


@app.post('/detect_all')
def detect_all(
              files: List[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  try:
    images = read_request_images(files)
    detections = full_pipeline(images)
    return detection_responce(detections, details)
  except Exception as e:
    return error_responce(e)
  

@app.post('/detect_ru')
def detect_ru(
              files: List[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  try:
    images = read_request_images(files)
    detections = ru_pipeline(images)
    return detection_responce(detections, details)
  except Exception as e:
    return error_responce(e)


def read_request_images(upload_files: List[UploadFile]):
  filenames = [upload_file.filename for upload_file in upload_files]
  logger.info(f'Processing files: {", ".join(filenames)}')

  images = []
  for upload_file in upload_files:
    try:
      images.append(read_image(upload_file.file.read()))
    finally:
      upload_file.file.close()

  return images


def detection_responce(images_with_detections: list, details: DetectionDetails):
  detections = list(map(lambda x: filter_image_detections(x, details), images_with_detections))
  return JSONResponse(
        status_code = status.HTTP_200_OK, 
        content={"detections": detections}
    )


def error_responce(e : Exception):
  exc_type, exc_value, exc_tb = sys.exc_info()
  traceback.print_exception(exc_type, exc_value, exc_tb)
  return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(e)},
    )
  

def filter_image_detections(image_detections: list, details: DetectionDetails):
  filtered_result = []

  # expected 'image_detections' structure: [image, [bboxes], [points], etc... , [texts]]
  # image = image_detections[0]
  detections = list(zip(*image_detections[1:]))  # skip image itself
  for detection in detections:
    bbox = detection[0]
    point = detection[1]
    # zone = detection[2]
    # region_id = detection[3]
    region_name = detection[4]
    count_line = detection[5]
    confidence = detection[6]
    text = detection[7]

    if details == DetectionDetails.FULL:
      filtered_result.append({
        "bbox": bbox,
        "point": point,
        "region_name": region_name,
        "count_line": count_line,
        "text": text,
        "confidence": confidence,
      })
    elif details == DetectionDetails.REGION:
      filtered_result.append({
        "region_name": region_name,
        "text": text
      })
    else:
      filtered_result.append({"text": text})

  return filtered_result
