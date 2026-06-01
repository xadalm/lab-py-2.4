from typing import Iterable

from src.task import Task


class ApiStubTaskSource:
    def get_tasks(self) -> Iterable[Task]:
        response = [
            {
                "id": "api-1",
                "description": "first from api",
                "priority": "high",
                "status": "new",
            },
            {
                "id": "api-2",
                "description": "second from api",
                "priority": "normal",
                "status": "in_progress",
            },
        ]
        return [
            Task(
                task_id=str(item["id"]),
                description=str(item["description"]),
                priority=str(item["priority"]),
                status=str(item["status"]),
            )
            for item in response
        ]
