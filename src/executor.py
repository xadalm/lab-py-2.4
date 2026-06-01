from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from src.handlers.task_handler import TaskHandler
from src.task_queue import TaskQueue
from src.task import Task

logger = logging.getLogger(__name__)


class AsyncExecutor:
    def __init__(self, handlers: Iterable[TaskHandler], concurrency: int = 5) -> None:
        self._handlers = list(handlers)
        self._semaphore = asyncio.Semaphore(concurrency)
        self._running: list[asyncio.Task] = []

    async def _run_handler(self, handler: TaskHandler, task: Task) -> None:
        async with self._semaphore:
            try:
                await handler.handle(task)
            except Exception:
                logger.exception("Ошибка при обработке задачи %s", task.id)

    async def run(self, tasks: TaskQueue) -> None:
        for task in tasks:
            for handler in self._handlers:
                try:
                    can = handler.can_handle(task)
                except Exception:
                    logger.exception("Ошибка проверки обработчика для %s", task.id)
                    continue
                if can:
                    self._running.append(asyncio.create_task(self._run_handler(handler, task)))
                    break

        if self._running:
            await asyncio.gather(*self._running)

    async def __aenter__(self) -> "AsyncExecutor":
        logger.info("Executor: start")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        logger.info("Executor: shutdown")
        if self._running:
            await asyncio.gather(*self._running, return_exceptions=True)
