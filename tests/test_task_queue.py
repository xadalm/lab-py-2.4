from src.task import Task
from src.task_queue import TaskQueue
from src.task_types import TaskPriority, TaskStatus


def test_task_queue_supports_repeated_iteration() -> None:
    queue = TaskQueue(
        [
            Task(task_id="t-1", description="first", priority="high"),
            Task(task_id="t-2", description="second", priority="low", status="in_progress"),
        ]
    )

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == ["t-1", "t-2"]
    assert second_pass == ["t-1", "t-2"]


def test_task_queue_filters_are_lazy_and_selective() -> None:
    queue = TaskQueue(
        [
            Task(task_id="t-1", description="first", priority="high"),
            Task(task_id="t-2", description="second", priority="normal", status="in_progress"),
            Task(task_id="t-3", description="third", priority="high", status="in_progress"),
        ]
    )

    high_priority = queue.filter_by_priority(TaskPriority.HIGH)
    in_progress = queue.filter_by_status(TaskStatus.IN_PROGRESS)

    assert type(high_priority).__name__ == "generator"
    assert type(in_progress).__name__ == "generator"
    assert [task.id for task in high_priority] == ["t-1", "t-3"]
    assert [task.id for task in in_progress] == ["t-2", "t-3"]