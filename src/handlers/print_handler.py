from __future__ import annotations

import asyncio
import logging

from src.task import Task

logger = logging.getLogger(__name__)


class PrintHandler:
    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        logger.info("PrintHandler: start handling %s", task.id)
        await asyncio.sleep(0)
        print(f"[{task.id}] priority={task.priority.value}; status={task.status.value}; text={task.description}")
        task.start()
        try:
            task.complete()
        except Exception:
            logger.exception("PrintHandler: error while completing %s", task.id)
            raise
        logger.info("PrintHandler: completed %s", task.id)
