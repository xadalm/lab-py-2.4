import json
from pathlib import Path
from typing import Any, Iterable

from src.task import Task
from src.task_types import TaskStatus


class FileTaskSource:
    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)

    def get_tasks(self) -> Iterable[Task]:
        raw_items: list[dict[str, Any]] = json.loads(self._file_path.read_text(encoding="utf-8"))
        tasks: list[Task] = []
        for item in raw_items:
            tasks.append(
                Task(
                    task_id=str(item["id"]),
                    description=str(item["description"]),
                    priority=str(item["priority"]),
                    status=str(item.get("status", TaskStatus.NEW.value)),
                )
            )
        return tasks
