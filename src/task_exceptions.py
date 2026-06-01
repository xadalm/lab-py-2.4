class TaskError(Exception):
    """Base exception for domain task errors."""


class TaskValidationError(TaskError, ValueError):
    """Raised when task data violates validation constraints."""


class TaskStateError(TaskError):
    """Raised when task state transition is not allowed."""