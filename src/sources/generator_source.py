from typing import Iterable

from src.task import Task
from src.task_types import TaskPriority


class GeneratedTaskSource:
    def __init__(self, count: int) -> None:
        self._count = count

    def get_tasks(self) -> Iterable[Task]:
        return [
            Task(
                task_id=f"gen-{index}",
                description=f"Generated task #{index}",
                priority=TaskPriority.NORMAL,
            )
            for index in range(1, self._count + 1)
        ]
