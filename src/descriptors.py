from __future__ import annotations

from src.task_exceptions import TaskValidationError
from src.task_types import TaskPriority


class BaseDescriptor:
    """Base class for data descriptors that validate assigned values."""

    def __set_name__(self, owner: type, name: str) -> None:
        self._storage_name = f"_{name}"

    def __get__(self, instance: object, owner: type | None = None) -> object:
        if instance is None:
            return self
        return getattr(instance, self._storage_name)

    def __set__(self, instance: object, value: object) -> None:
        setattr(instance, self._storage_name, self.validate(value))

    def validate(self, value: object) -> object:
        return value


class IdentifierDescriptor(BaseDescriptor):
    """Validates task identifier format and non-empty invariant."""

    def validate(self, value: object) -> str:
        if not isinstance(value, str):
            raise TaskValidationError("task_id must be a string")

        normalized = value.strip()
        if not normalized:
            raise TaskValidationError("task_id must not be empty")
        if len(normalized) > 64:
            raise TaskValidationError("task_id must be at most 64 characters")
        if not all(ch.isalnum() or ch in "-_" for ch in normalized):
            raise TaskValidationError("task_id contains invalid characters")
        return normalized


class DescriptionDescriptor(BaseDescriptor):
    """Validates task description shape and limits."""

    def validate(self, value: object) -> str:
        if not isinstance(value, str):
            raise TaskValidationError("description must be a string")

        normalized = value.strip()
        if not normalized:
            raise TaskValidationError("description must not be empty")
        if len(normalized) > 500:
            raise TaskValidationError("description must be at most 500 characters")
        return normalized


class PriorityDescriptor(BaseDescriptor):
    """Validates and normalizes task priority into TaskPriority enum."""

    def validate(self, value: object) -> TaskPriority:
        if isinstance(value, TaskPriority):
            return value
        if isinstance(value, str):
            try:
                return TaskPriority(value.lower())
            except ValueError as exc:
                raise TaskValidationError("priority must be one of: low, normal, high") from exc
        raise TaskValidationError("priority must be TaskPriority or string")


class StaticLabelDescriptor:
    """Non-data descriptor used to demonstrate descriptor precedence."""

    def __init__(self, label: str) -> None:
        self._label = label

    def __get__(self, instance: object, owner: type | None = None) -> str:
        return self._label


class ProtectedTextDescriptor(BaseDescriptor):
    """Simple data descriptor for descriptor behavior tests."""

    def validate(self, value: object) -> str:
        if not isinstance(value, str):
            raise TaskValidationError("value must be a string")
        return value


class DescriptorShowcase:
    """Class used in tests to show data vs non-data descriptor differences."""

    non_data_label = StaticLabelDescriptor("shared-label")
    protected_text = ProtectedTextDescriptor()

    def __init__(self) -> None:
        self.protected_text = "initial"