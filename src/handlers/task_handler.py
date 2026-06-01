from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.task import Task


@runtime_checkable
class TaskHandler(Protocol):
    def can_handle(self, task: Task) -> bool:
        ...

    async def handle(self, task: Task) -> None:
        ...
