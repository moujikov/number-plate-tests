import asyncio
from typing import Any
from contextlib import asynccontextmanager
from collections.abc import Awaitable
from urllib import parse as urlparse

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer
from numpy import ndarray

from common.logging import logger as common_logger
from common.types import DetectCountry
from image_processing import jpeg, number_plates
from rest_server.common.logging import logger, log_request, log_exception
from rest_server.common.auth import check_authorized
from . import DETECT_COUNTRIES, MAX_CONCURRENT_REQUESTS


### Resources initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
  # Startup
  detect_countries = [DetectCountry(c.strip().upper()) for c in DETECT_COUNTRIES.split(',')]
  # Preloading models to avoid first request latency
  await number_plates.setup_async(*detect_countries)

  common_logger.info('Server ready')
  yield
  
  # Shutdown


### FastAPI app
app = FastAPI(lifespan=lifespan)
auth = OAuth2PasswordBearer(tokenUrl="access_token", auto_error=False)
concurrent_requests = 0


### Middlewares for logging requests
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
  return await log_request(request, call_next)

app.add_middleware(CorrelationIdMiddleware)
  

### API endpoints

@app.get('/healthcheck')
async def healthcheck():
  return {"status": "ok"}


@app.post('/detect')
async def detect(
           access_token: str = Depends(auth),
           images: list[UploadFile] = File(...)
          ):
  check_authorized(access_token)
  return await _with_concurrency_check(_detect(images))



### Helper functions

async def _with_concurrency_check(task: Awaitable) -> Any:
  global concurrent_requests
  concurrent_requests += 1
  
  try:
    if concurrent_requests > MAX_CONCURRENT_REQUESTS > 0:
      logger.warning(f'Too many concurrent requests (limit: {MAX_CONCURRENT_REQUESTS})')
      raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS)
      
    return await task
  finally:
    concurrent_requests -= 1


async def _detect(upload_files: list[UploadFile]) -> dict[str, Any]:
  names = [urlparse.unquote(f.filename) if f.filename else '' for f in upload_files]
  logger.debug(f'Processing files: {", ".join(names)}')

  try:
    images = await _read_request_images(upload_files)
    results = await number_plates.detect_async(images, names = names)

    number_plates_digest: list[str] = []
    for image_detections in results:
      name = image_detections.name
      plates = [number_plate.text for number_plate in image_detections.number_plates]
      number_plates_digest.append(f'{name} – {", ".join(plates)}')
    
    logger.info(f'Detected number plates: {"; ".join(number_plates_digest)}')
    logger.debug(f'Full detection results: {"; ".join([str(r) for r in results])}')

    return {'images': results}
  except Exception as e:
    log_exception(e)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))


async def _read_request_images(upload_files: list[UploadFile]) -> list[ndarray]:
  images: list[ndarray] = []
  for upload_file in upload_files:
    try:
      jpg_image = await upload_file.read()
      decoded_image = await jpeg.read_image_async(jpg_image)
      images.append(decoded_image)
    finally:
      await upload_file.close()

  return images
