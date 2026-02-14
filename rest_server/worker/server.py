import os
import urllib
from threading import Lock
from typing import Callable

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer

import common.logging as general_logging
import rest_server.common.logging as server_logging
import rest_server.common.auth as server_auth
from common.data import DetectionDetails
from image_processing.jpeg import read_image
from image_processing.pipelines import full_pipeline, ru_pipeline


### Configuration from environment variables

MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 0))
if MAX_CONCURRENT_REQUESTS > 0:
  general_logging.info(f'Setting max concurrent requests to {MAX_CONCURRENT_REQUESTS}.')


### Preloading models to avoid first request latency
general_logging.info('Preloading models...')
full_pipeline([])
ru_pipeline([])


### FastAPI app
app = FastAPI()
auth = OAuth2PasswordBearer(tokenUrl="access_token", auto_error=False)
check_concurrency_lock = Lock()
concurrent_requests = 0


### Middlewares for logging requests
@app.middleware("http")
async def log_request(request: Request, call_next):
  return await server_logging.log_request(request, call_next)

app.add_middleware(CorrelationIdMiddleware)


### API endpoints

@app.get('/healthcheck')
def healthcheck():
  return {"status": "ok"}


@app.post('/detect_all')
def detect_all(
              access_token: str = Depends(auth),
              images: list[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  server_auth.check_authorized(access_token)
  return with_concurrency_check(lambda: _detect(full_pipeline, images, details))


@app.post('/detect_ru')
def detect_ru(
              access_token: str = Depends(auth),
              images: list[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  server_auth.check_authorized(access_token)
  return with_concurrency_check(lambda: _detect(ru_pipeline, images, details))


### Helper functions


def with_concurrency_check(callable: Callable):
  global concurrent_requests

  if MAX_CONCURRENT_REQUESTS > 0:
    with check_concurrency_lock:
      if concurrent_requests < MAX_CONCURRENT_REQUESTS: 
        concurrent_requests += 1
      else: 
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS)
      
  try:
    return callable()
  finally:
    if MAX_CONCURRENT_REQUESTS > 0: concurrent_requests -= 1


def _detect(pipeline: Callable, upload_files: list[UploadFile], details: DetectionDetails):
  filenames = [urllib.parse.unquote(f.filename) for f in upload_files]
  server_logging.info(f'Processing files: {", ".join(filenames)}')

  try:
    images = _read_request_images(upload_files)
    detections = pipeline(images)
    return _detection_response(filenames, detections, details)
  except Exception as e:
    server_logging.log_exception(e)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))


def _read_request_images(upload_files: list[UploadFile]):
  images = []
  for upload_file in upload_files:
    try:
      content = upload_file.file.read()
      images.append(read_image(content))
    finally:
      upload_file.file.close()

  return images


def _detection_response(filenames: list[str], detections: list, details: DetectionDetails):
  return {"images": [_filter_image_detections(pair[0], pair[1], details) 
                     for pair in zip(filenames, detections)]}


def _filter_image_detections(image_name: str, image_detections: list, details: DetectionDetails):
  filtered_detections = []

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
      filtered_detections.append({
        "bbox": bbox,
        "point": point,
        "region_name": region_name,
        "count_line": count_line,
        "text": text,
        "confidence": confidence,
      })
    elif details == DetectionDetails.REGION:
      filtered_detections.append({
        "region_name": region_name,
        "text": text
      })
    else:
      filtered_detections.append({"text": text})

  return {
          "image": image_name,
          "detections": filtered_detections
         }
