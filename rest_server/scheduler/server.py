import asyncio
import contextlib
import contextlib
import urllib

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile,  status
from fastapi.security import OAuth2PasswordBearer
from asgi_correlation_id import CorrelationIdMiddleware

from rest_server.common.logging import logger, log_request, log_exception
from rest_server.common.auth import check_authorized
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
              images: list[UploadFile] = File(...),
              details: DetectionDetails = Form(DetectionDetails.NONE)
              ):
  check_authorized(access_token)
  return await forward_request("detect", images, details)



### Helper functions

async def forward_request(path: str, upload_files: list[UploadFile], details: DetectionDetails):
  filenames = [urllib.parse.unquote(f.filename) for f in upload_files]
  logger.info(f'Processing files: {", ".join(filenames)}')

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

    logger.debug(f'Returning detection results: {", ".join([str(r) for r in results])}')
    return {"images": results}

  except Exception as e:
    log_exception(e)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))
