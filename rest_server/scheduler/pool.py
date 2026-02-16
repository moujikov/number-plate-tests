import os
import time
from asyncio import Event, Queue

import common.logging as general_logging
import rest_server.common.logging as server_logging
from .task import WorkerTask
from .worker import Worker


class WorkersPool:
  def __init__(self):
    self._workers : list[Worker] = []
    self._queue : Queue[WorkerPromise] = Queue()

  def add_worker(self, worker: Worker):
    self._workers.append(worker)

  async def close(self):
    general_logging.info(f"Closing all workers in the pool")
    for worker in self._workers:
      await worker.close()

  async def schedule_task(self, task: WorkerTask) -> any:
    worker = None
    try:
      worker = await self._take_worker(task)
      started = time.perf_counter()
      result = await task.execute_on(worker)
      waited = round((time.perf_counter() - started) * 1000)
      server_logging.info(f"After {waited}ms got results from worker {worker.short_str} for {task}")
      return result
    finally:
      self.__free_worker(worker) if worker else None
      
  async def _take_worker(self, task: WorkerTask) -> Worker:
    worker = self.__find_free_worker(task)
    if worker:
      server_logging.info(f"Using free worker {worker.full_str} for {task}")
      worker.set_busy()
      return worker

    promise = WorkerPromise(task)
    self._queue.put_nowait(promise)

    return await promise.wait_worker()

  def __free_worker(self, worker: Worker):
    if not self._queue.empty():
      promise = self._queue.get_nowait()
      server_logging.info(
        f"Passing worker {worker.short_str} to the next waiting request with {promise.task}")
      promise.fulfill(worker)
    else:
      server_logging.info(f"Returning worker {worker.short_str} to the pool")
      worker.set_free()
    
  def __find_free_worker(self, task: WorkerTask) -> Worker | None:
    if not any(worker.is_active for worker in self._workers):
      raise Exception("No active workers in the pool")    

    for worker in self._workers:
      if worker.is_free:
        return worker

    return None


class RoundRobinWorkersPool(WorkersPool):
  async def _take_worker(self, task: WorkerTask) -> Worker:
    worker = await super()._take_worker(task)
    self._workers.remove(worker)
    self._workers.append(worker)
    return worker


class WorkerPromise:
  def __init__(self, task: WorkerTask):
    self.task = task
    self.__event = Event()
    self.__worker: Worker | None = None

  async def wait_worker(self) -> Worker:
    started = time.perf_counter()
    server_logging.info(f"Waiting for a free worker for {self.task}...")
    await self.__event.wait()

    waited = time.perf_counter() - started
    server_logging.info(
      f"After {waited:.2f}s got free worker {self.__worker.full_str} for {self.task}")

    return self.__worker

  def fulfill(self, worker: Worker):
    self.__worker = worker
    self.__event.set()


class WorkersPoolConfigurator:
  WORKER_URL_PREFIX = "WORKER_URL_"
  WORKER_ACCESS_TOKEN_PREFIX = "WORKER_ACCESS_TOKEN_"

  def __init__(self, pool: WorkersPool):
    self.pool = pool

  def read_settings_from_environment(self):
    for id in sorted([key.removeprefix(self.WORKER_URL_PREFIX) 
               for key in os.environ.keys() 
               if key.startswith(self.WORKER_URL_PREFIX)]):
      url = os.getenv(f"{self.WORKER_URL_PREFIX}{id}", "").strip()
      token = os.getenv(f"{self.WORKER_ACCESS_TOKEN_PREFIX}{id}", "").strip()
      if url: 
        self._add_worker(id, url, token)

  def _add_worker(self, id: int, url: str, token: str):
    worker = Worker(id, url, token if token else None)
    general_logging.info(
                        f"Adding worker {worker.full_str}"
                        f"{' with access token' if token else ''} to the pool"
                        )
    self.pool.add_worker(worker)
