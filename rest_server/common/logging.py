import sys
import time
import logging
import traceback
import asgi_correlation_id
from fastapi import Request

from common import LOG_LEVEL

stream_handler = logging.StreamHandler()
stream_handler.addFilter(asgi_correlation_id.CorrelationIdFilter(uuid_length=4))
stream_handler.setFormatter(logging.Formatter(
  fmt = "%(asctime)s [%(correlation_id)s] %(levelname)s - %(message)s",
  datefmt='%Y-%m-%d %H:%M:%S'))

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream_handler)
logger.propagate = False


async def log_request(request: Request, call_next):
  if request.url.path != "/healthcheck":
    logger.info(f"Processing request: {request.method} {request.url.path} from {request.client.host}")
    start_time = time.perf_counter()
  response = await call_next(request)
  if request.url.path != "/healthcheck":
    process_time = round((time.perf_counter() - start_time) * 1000)
    logger.info(f"Completed in {process_time}ms with status {response.status_code}")
  return response


def log_exception(e : Exception):
  exc_type, exc_value, exc_tb = sys.exc_info()
  traceback.print_exception(exc_type, exc_value, exc_tb)
