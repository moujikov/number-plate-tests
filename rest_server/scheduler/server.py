import os
import sys
from threading import Lock
import traceback
import time
import logging
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.responses import ORJSONResponse as JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Callable, List
from enum import Enum


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


### FastAPI app
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


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
  return forward_request("detect_all", files, details)


@app.post('/detect_ru')
def detect_ru(
              access_token: str = Depends(oauth2_scheme),
              files: List[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  check_authorized(access_token)
  return forward_request("detect_ru", files, details)



### Helper functions

def check_authorized(access_token: str):
  if ACCESS_TOKEN and access_token != ACCESS_TOKEN:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})


def forward_request(path: str, files: List[UploadFile], details: DetectionDetails):
  try:
      return JSONResponse(
        status_code = status.HTTP_200_OK, 
        content={"detections": {}}
    )
  except Exception as e:
    return _error_responce(e)


def _error_responce(e : Exception):
  exc_type, exc_value, exc_tb = sys.exc_info()
  traceback.print_exception(exc_type, exc_value, exc_tb)
  return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(e)},
    )
