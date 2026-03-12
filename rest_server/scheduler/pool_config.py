import os

from common.logging import logger
from .worker import Worker
from .pool import WorkersPool


class WorkersPoolConfigurator:
  WORKER_URL_PREFIX = 'WORKER_URL_'
  WORKER_ACCESS_TOKEN_PREFIX = 'WORKER_ACCESS_TOKEN_'

  def __init__(self, pool: WorkersPool):
    self.pool = pool

  def read_settings_from_environment(self):
    for id in sorted([int(key.removeprefix(self.WORKER_URL_PREFIX))
               for key in os.environ.keys() 
               if key.startswith(self.WORKER_URL_PREFIX)]):
      url = os.getenv(f'{self.WORKER_URL_PREFIX}{id}', '').strip()
      if url:
        token = os.getenv(f'{self.WORKER_ACCESS_TOKEN_PREFIX}{id}', '').strip()
        if token:
          worker = self._add_worker(id, url, token)
          logger.info(f'Added worker {worker.full_str} with access token from environment variable')
        else:
          try:
            with open(f'/run/secrets/worker-{id}_access_token') as f:
              token = f.read().strip()
              worker = self._add_worker(id, url, token)
              logger.info(f'Added worker {worker.full_str} with access token from secret')
          except FileNotFoundError:
            worker = self._add_worker(id, url)
            logger.info(f'Added worker {worker.full_str} without access token')

  def _add_worker(self, id: int, url: str, token: str | None = None) -> Worker:
    worker = Worker(id, url, token)
    self.pool.add_worker(worker)
    return worker
