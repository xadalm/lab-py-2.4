from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator

from src.task import Task
from src.task_types import TaskPriority, TaskStatus


class TaskQueue(list[Task]):
    def __init__(self, tasks: Iterable[Task] = ()) -> None:
        super().__init__(tasks)

    def add_task(self, task: Task) -> None:
        self.append(task)

    def extend_tasks(self, tasks: Iterable[Task]) -> None:
        self.extend(tasks)

    def filter(self, predicate: Callable[[Task], bool]) -> Iterator[Task]:
        return (task for task in self if predicate(task))

    def filter_by_status(self, status: TaskStatus) -> Iterator[Task]:
        return self.filter(lambda task: task.status is status)

    def filter_by_priority(self, priority: TaskPriority) -> Iterator[Task]:
        return self.filter(lambda task: task.priority is priority)