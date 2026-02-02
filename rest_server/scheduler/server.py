import sys
import traceback

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile,  status
from fastapi.responses import ORJSONResponse as JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List

from common.data import DetectionDetails
from common.logging import logger
from rest_server.common.auth import check_authorized
from rest_server.common.logging import log_request as _log_request



### FastAPI app
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token", auto_error=False)


### Middleware for logging requests execution time
@app.middleware("http")
async def log_request(request: Request, call_next):
  return await _log_request(request, call_next)



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


def forward_request(path: str, files: List[UploadFile], details: DetectionDetails):
  try:
      return JSONResponse(
        status_code = status.HTTP_200_OK, 
        content={"detections": {}}
    )
  except Exception as e:
    return _error_response(e)


def _error_response(e : Exception):
  exc_type, exc_value, exc_tb = sys.exc_info()
  traceback.print_exception(exc_type, exc_value, exc_tb)
  return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(e)},
    )
