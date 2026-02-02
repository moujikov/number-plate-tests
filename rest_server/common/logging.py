import time
from fastapi import Request

from common.logging import logger

async def log_request(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  process_time = round((time.time() - start_time) * 1000)
  logger.info(f"Completed in {process_time}ms with status {response.status_code}")
  return response
