import asyncio
from collections.abc import Awaitable
import os
from typing import Collection
import urllib

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer

import common.logging as general_logging
import rest_server.common.logging as server_logging
import rest_server.common.auth as server_auth
from common.data import DetectionDetails
from image_processing.jpeg import read_image
import image_processing.pipelines as pipelines


### Configuration from environment variables

MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 0))
if MAX_CONCURRENT_REQUESTS > 0:
  general_logging.info(f'Setting max concurrent requests to {MAX_CONCURRENT_REQUESTS}.')


### Preloading models to avoid first request latency
DETECT_COUNTRIES = os.getenv('DETECT_COUNTRIES', 'RU')
detect_countries = [pipelines.DetectCountry(c.strip().upper()) for c in DETECT_COUNTRIES.split(',')]
pipelines.setup_pipeline(detect_countries)


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
    detections = await asyncio.to_thread(pipelines.pipeline, images)
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
  return {"images": [_filter_image_detections(pair[0], pair[1], details) 
                     for pair in zip(filenames, detections)]}


def _filter_image_detections(image_name: str, image_detections: list, details: DetectionDetails):
  filtered_detections = []

  # expected 'image_detections' structure: [image, [bboxes], [points], etc... , [texts]]
  # image = image_detections[0]
  detections = list(zip(*image_detections[1:]))  # skip image itself
  for detection in detections:
    # expected order of 'detection' elements: [bbox, point, zone, region_id, region_name, count_line, confidence, text]

    filtered_detection = {}

    if details == DetectionDetails.FULL or details == DetectionDetails.CONFIDENCE:
      confidences = {"box": round(float(detection[0][4]), 6)}
      if len(pipelines.configured_countries) > 1:
        confidences["region"] = round(float(detection[6][0]), 6)
      filtered_detection["confidences"] = confidences

    if details == DetectionDetails.FULL:
      filtered_detection["box"] = __int_points(detection[1])

    if len(pipelines.configured_countries) > 1:
      filtered_detection["region"] = detection[4]
    
    filtered_detection["text"] = detection[7]
    filtered_detections.append(filtered_detection)

  return {
          "image": image_name,
          "detections": filtered_detections
         }

def __int_points(points: Collection):
  if isinstance(points, Collection):
    return [__int_points(x) for x in points]
  
  return round(points)
