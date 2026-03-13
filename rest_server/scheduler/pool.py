import time

from asyncio import Event, Queue
from typing import Any

from common.logging import logger as logger
from rest_server.common.logging import logger as server_logger
from .task import WorkerTask
from .worker import Worker


class WorkersPool:
  def __init__(self):
    self._workers : list[Worker] = []
    self._queue : Queue[WorkerPromise] = Queue()

  def add_worker(self, worker: Worker):
    self._workers.append(worker)

  async def close(self):
    logger.info(f"Closing all workers in the pool")
    for worker in self._workers:
      await worker.close()

  async def schedule_task(self, task: WorkerTask) -> dict[str, Any]:
    worker = None
    try:
      worker = await self._take_worker(task)
      started = time.perf_counter()
      result = await task.execute_on(worker)
      waited = time.perf_counter() - started
      server_logger.debug(f"After {waited:.2f}s got results from worker {worker.short_str} for {task}")
      return result
    finally:
      self.__free_worker(worker) if worker else None
      
  async def _take_worker(self, task: WorkerTask) -> Worker:
    worker = self.__find_free_worker(task)
    if worker:
      server_logger.debug(f"Using worker {worker.full_str} for {task}")
      worker.set_busy()
      return worker

    promise = WorkerPromise(task)
    self._queue.put_nowait(promise)

    return await promise.wait_worker()

  def __free_worker(self, worker: Worker):
    if not self._queue.empty():
      promise = self._queue.get_nowait()
      server_logger.debug(
        f"Passing freed worker {worker.short_str} to {promise.task}")
      promise.fulfill(worker)
    else:
      server_logger.debug(f"Returning worker {worker.short_str} to the pool")
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
    server_logger.debug(f"Waiting for worker for {self.task}...")
    await self.__event.wait()

    if not self.__worker:
      raise Exception("WorkerPromise fulfilled without worker")

    waited = time.perf_counter() - started
    server_logger.debug(
      f"After {waited:.2f}s got worker {self.__worker.full_str} for {self.task}")

    return self.__worker

  def fulfill(self, worker: Worker):
    self.__worker = worker
    self.__event.set()
