from __future__ import annotations

import asyncio

from src.executor import AsyncExecutor
from src.handlers.task_handler import TaskHandler
from src.task import Task
from src.task_queue import TaskQueue


def test_handler_protocol_and_runtime_check() -> None:
    class SimpleHandler:
        def can_handle(self, task: Task) -> bool:
            return True

        async def handle(self, task: Task) -> None:
            return None

    handler = SimpleHandler()

    # runtime check against Protocol should accept this handler
    assert isinstance(handler, TaskHandler)


def test_async_executor_runs_handlers_and_marks_tasks_done() -> None:
    results: list[str] = []

    class MarkingHandler:
        def can_handle(self, task: Task) -> bool:
            return True

        async def handle(self, task: Task) -> None:
            await asyncio.sleep(0)
            task.start()
            task.complete()
            results.append(task.id)

    tasks = TaskQueue([Task(task_id="t-1", description="do", priority="low")])

    async def run_exec() -> None:
        async with AsyncExecutor(handlers=[MarkingHandler()], concurrency=2) as executor:
            await executor.run(tasks)

    asyncio.run(run_exec())

    assert results == ["t-1"]
    assert tasks[0].is_done
