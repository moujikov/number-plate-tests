import asyncio
import contextlib
import contextlib
import urllib

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer
from asgi_correlation_id import CorrelationIdMiddleware

import rest_server.common.logging as server_logging
import rest_server.common.auth as server_auth
from common.data import DetectionDetails
from .task import ImageDetectionWorkerTask
from .pool import RoundRobinWorkersPool, WorkersPoolConfigurator

### Resources initialization
workers = RoundRobinWorkersPool()

  
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    workers_configurator = WorkersPoolConfigurator(workers)
    workers_configurator.read_settings_from_environment()

    yield
    # Shutdown    
    await workers.close()


### FastAPI app
app = FastAPI(lifespan=lifespan)
auth = OAuth2PasswordBearer(tokenUrl="access_token", auto_error=False)


### Middlewares for logging requests
@app.middleware("http")
async def log_request(request: Request, call_next):
  return await server_logging.log_request(request, call_next)

app.add_middleware(CorrelationIdMiddleware)


### API endpoints

@app.post('/detect_all')
async def detect_all(
              access_token: str = Depends(auth),
              images: list[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  server_auth.check_authorized(access_token)
  return await forward_request("detect_all", images, details)

@app.post('/detect_ru')
async def detect_ru(
              access_token: str = Depends(auth),
              images: list[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.FULL)
              ):
  server_auth.check_authorized(access_token)
  return await forward_request("detect_ru", images, details)



### Helper functions

async def forward_request(path: str, upload_files: list[UploadFile], details: DetectionDetails):
  filenames = [urllib.parse.unquote(f.filename) for f in upload_files]
  server_logging.info(f'Processing files: {", ".join(filenames)}')

  try:
    async with asyncio.TaskGroup() as tg:
      tasks = []
      for file in upload_files:
        t = ImageDetectionWorkerTask(path, details)
        name = urllib.parse.unquote(file.filename)
        t.add_image(name, file.content_type, await file.read())
        tasks.append(tg.create_task(workers.schedule_task(t), name = name))

    results = []
    for task in tasks:
      result = task.result()
      if "images" in result:
        results.extend(result["images"])
      else:
        results.append({
          "image": task.get_name(), 
          "error": result
        })

    return {"images": results}

  except Exception as e:
    server_logging.log_exception(e)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))
