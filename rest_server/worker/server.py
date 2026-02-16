import asyncio
from collections.abc import Awaitable
import os
import urllib
from threading import Lock
from typing import Callable

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import ORJSONResponse

import common.logging as general_logging
import rest_server.common.logging as server_logging
import rest_server.common.auth as server_auth
from common.data import DetectionDetails
from image_processing.jpeg import read_image
from image_processing.pipelines import ( pipeline,
                                         setup_full_pipeline, 
                                         setup_ru_by_pipeline, 
                                         setup_ru_pipeline )


### Configuration from environment variables

MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 0))
if MAX_CONCURRENT_REQUESTS > 0:
  general_logging.info(f'Setting max concurrent requests to {MAX_CONCURRENT_REQUESTS}.')


### Preloading models to avoid first request latency
DETECT_COUNTRIES = os.getenv('DETECT_COUNTRIES', 'RU').upper()
if DETECT_COUNTRIES == 'ALL':
  general_logging.info('Preloading models for ALL number plate types...')
  setup_full_pipeline()
elif DETECT_COUNTRIES == 'RU_BY':
  general_logging.info('Preloading models for RU and BY number plates...')
  setup_ru_by_pipeline()
elif DETECT_COUNTRIES == 'RU':
  general_logging.info('Preloading models for RU number plates...')
  setup_ru_pipeline()
else:
  general_logging.error(
    f'Unknown value for DETECT_COUNTRIES: {DETECT_COUNTRIES}. '
    f'Supported values are: ALL, RU_BY, RU.')


### FastAPI app
app = FastAPI()
auth = OAuth2PasswordBearer(tokenUrl="access_token", auto_error=False)
concurrent_requests = 0


### Middlewares for logging requests
@app.middleware("http")
async def log_request(request: Request, call_next):
  return await server_logging.log_request(request, call_next)

app.add_middleware(CorrelationIdMiddleware)


### API endpoints

@app.get('/healthcheck')
async def healthcheck():
  return {"status": "ok"}


@app.post('/detect')
async def detect(
           access_token: str = Depends(auth),
           images: list[UploadFile] = File(...),
           details: DetectionDetails = Form(DetectionDetails.NONE)
          ):
  server_auth.check_authorized(access_token)
  return await with_concurrency_check(_detect, images, details)



### Helper functions


async def with_concurrency_check(awaitable: Awaitable, /, *args, **kwargs):
  global concurrent_requests
  concurrent_requests += 1
  
  try:
    if concurrent_requests > MAX_CONCURRENT_REQUESTS > 0:
      raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS)
      
    return await awaitable(*args, **kwargs)
  finally:
    concurrent_requests -= 1


async def _detect(upload_files: list[UploadFile], details: DetectionDetails):
  filenames = [urllib.parse.unquote(f.filename) for f in upload_files]
  server_logging.info(f'Processing files: {", ".join(filenames)}')

  try:
    images = await _read_request_images(upload_files)
    detections = await asyncio.to_thread(pipeline, images)
    return _detection_response(filenames, detections, details)
  except Exception as e:
    server_logging.log_exception(e)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))


async def _read_request_images(upload_files: list[UploadFile]):
  images = []
  for upload_file in upload_files:
    try:
      jpg_image = await upload_file.read()
      decoded_image = await asyncio.to_thread(read_image, jpg_image)
      images.append(decoded_image)
    finally:
      await upload_file.close()

  return images


def _detection_response(filenames: list[str], detections: list, details: DetectionDetails):
  # Important to use 'ORJSONResponse' to marshal eventual NumPy numeric types in detection results
  return ORJSONResponse({
                         "images": [_filter_image_detections(pair[0], pair[1], details) 
                                    for pair in zip(filenames, detections)]
                        })


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
