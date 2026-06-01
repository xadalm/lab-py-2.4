from __future__ import annotations

from datetime import datetime

from src.descriptors import DescriptionDescriptor, IdentifierDescriptor, PriorityDescriptor
from src.task_exceptions import TaskStateError, TaskValidationError
from src.task_types import TaskPriority, TaskStatus


class Task:
    """Domain model with validated attributes and protected status transitions."""

    task_id = IdentifierDescriptor()
    description = DescriptionDescriptor()
    priority = PriorityDescriptor()

    _ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
        TaskStatus.NEW: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
        TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.CANCELLED},
        TaskStatus.DONE: set(),
        TaskStatus.CANCELLED: set(),
    }

    def __init__(
        self,
        task_id: str,
        description: str,
        priority: TaskPriority | str,
        status: TaskStatus | str = TaskStatus.NEW,
        created_at: datetime | None = None,
    ) -> None:
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self._status = self._normalize_status(status)
        self._created_at = created_at or datetime.now()

    @property
    def id(self) -> str:
        """Compatibility alias for previous platform version."""
        return self.task_id

    @property
    def created_at(self) -> datetime:
        """Creation timestamp is immutable after object construction."""
        return self._created_at

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, new_status: TaskStatus | str) -> None:
        target_status = self._normalize_status(new_status)
        if target_status == self._status:
            return

        allowed = self._ALLOWED_TRANSITIONS[self._status]
        if target_status not in allowed:
            raise TaskStateError(
                f"Illegal transition: {self._status.value} -> {target_status.value}"
            )
        self._status = target_status

    @property
    def is_done(self) -> bool:
        """Computed property that reflects task completion."""
        return self.status is TaskStatus.DONE

    @property
    def is_ready_for_execution(self) -> bool:
        """Task is ready to execute only if it is not started yet."""
        return self.status is TaskStatus.NEW

    def start(self) -> None:
        self.status = TaskStatus.IN_PROGRESS

    def complete(self) -> None:
        self.status = TaskStatus.DONE

    def cancel(self) -> None:
        self.status = TaskStatus.CANCELLED

    @staticmethod
    def _normalize_status(value: TaskStatus | str) -> TaskStatus:
        if isinstance(value, TaskStatus):
            return value
        if isinstance(value, str):
            try:
                return TaskStatus(value.lower())
            except ValueError as exc:
                raise TaskValidationError(
                    "status must be one of: new, in_progress, done, cancelled"
                ) from exc
        raise TaskValidationError("status must be TaskStatus or string")