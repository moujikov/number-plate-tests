import os
import sys
from enum import Enum
from threading import Lock
import traceback
import time
import logging
from typing import Callable, List

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.responses import ORJSONResponse as JSONResponse
from fastapi.security import OAuth2PasswordBearer

from image_processing.jpeg import read_image
from image_processing.pipelines import full_pipeline, ru_pipeline


class DetectionDetails(str, Enum):
  FULL = "full"
  REGION = "region"
  NONE = "none"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


### Configuration from environment variables

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN') 
if ACCESS_TOKEN:
  logger.info('Using access token from environment variable.')

MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 0))
if MAX_CONCURRENT_REQUESTS > 0:
  logger.info(f'Setting max concurrent requests to {MAX_CONCURRENT_REQUESTS}.')


### FastAPI app
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

check_concurrency_lock = Lock()
concurrent_requests = 0


### Middleware for logging requests execution time
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000)
    logger.info(f"Completed in {process_time}ms with status {response.status_code}")
    return response



### API endpoints

@app.post('/detect_all')
def detect_all(
              access_token: str = Depends(oauth2_scheme),
              files: List[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  check_authorized(access_token)
  return with_concurrency_check(lambda: _detect(full_pipeline, files, details))


@app.post('/detect_ru')
def detect_ru(
              access_token: str = Depends(oauth2_scheme),
              files: List[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  check_authorized(access_token)
  return with_concurrency_check(lambda: _detect(ru_pipeline, files, details))



### Helper functions

def check_authorized(access_token: str):
  if ACCESS_TOKEN and access_token != ACCESS_TOKEN:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})


def with_concurrency_check(callable: Callable):
  global concurrent_requests

  if MAX_CONCURRENT_REQUESTS > 0:
    with check_concurrency_lock:
      if concurrent_requests < MAX_CONCURRENT_REQUESTS: concurrent_requests += 1
      else: raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS)
      
  try:
    return callable()
  finally:
    if MAX_CONCURRENT_REQUESTS > 0: concurrent_requests -= 1


def _detect(pipeline: Callable, files: List[UploadFile], details: DetectionDetails):
  try:
    images = _read_request_images(files)
    detections = pipeline(images)
    return _detection_responce(detections, details)
  except Exception as e:
    return _error_responce(e)


def _read_request_images(upload_files: List[UploadFile]):
  filenames = [upload_file.filename for upload_file in upload_files]
  logger.info(f'Processing files: {", ".join(filenames)}')

  images = []
  for upload_file in upload_files:
    try:
      content = upload_file.file.read()
      images.append(read_image(content))
    finally:
      upload_file.file.close()

  return images


def _detection_responce(images_with_detections: list, details: DetectionDetails):
  detections = list(map(lambda x: _filter_image_detections(x, details), images_with_detections))
  return JSONResponse(
        status_code = status.HTTP_200_OK, 
        content={"detections": detections}
    )


def _error_responce(e : Exception):
  exc_type, exc_value, exc_tb = sys.exc_info()
  traceback.print_exception(exc_type, exc_value, exc_tb)
  return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(e)},
    )


def _filter_image_detections(image_detections: list, details: DetectionDetails):
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
