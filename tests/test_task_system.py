from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.descriptors import DescriptorShowcase
from src.main import main
from src.task_exceptions import TaskStateError, TaskValidationError
from src.task_types import TaskPriority, TaskStatus
from src.sources.api_stub_source import ApiStubTaskSource
from src.sources.file_source import FileTaskSource
from src.sources.generator_source import GeneratedTaskSource
from src.task import Task
from src.task_receiver import TaskReceiver
from src.task_source import TaskSource


def test_task_model_validates_and_normalizes_base_fields() -> None:
    task = Task(task_id=" t-1 ", description="  first task  ", priority="high")

    assert task.id == "t-1"
    assert task.description == "first task"
    assert task.priority is TaskPriority.HIGH
    assert task.status is TaskStatus.NEW


def test_task_model_rejects_invalid_field_values() -> None:
    with pytest.raises(TaskValidationError, match="task_id"):
        Task(task_id="bad id", description="ok", priority="low")

    with pytest.raises(TaskValidationError, match="description"):
        Task(task_id="ok-id", description="", priority="low")

    with pytest.raises(TaskValidationError, match="priority"):
        Task(task_id="ok-id", description="ok", priority="urgent")


def test_task_model_rejects_invalid_initial_status() -> None:
    with pytest.raises(TaskValidationError, match="status"):
        Task(task_id="t-1", description="valid", priority="normal", status="blocked")


def test_created_at_property_is_read_only() -> None:
    task = Task(task_id="t-1", description="valid", priority="normal")

    with pytest.raises(AttributeError):
        task.created_at = task.created_at  # type: ignore[misc]


def test_task_status_transition_happy_path() -> None:
    task = Task(task_id="t-2", description="pipeline", priority="normal")

    task.start()
    task.complete()

    assert task.status is TaskStatus.DONE
    assert task.is_done is True
    assert task.is_ready_for_execution is False


def test_task_status_prevents_illegal_transition() -> None:
    task = Task(task_id="t-3", description="pipeline", priority="normal", status="done")

    with pytest.raises(TaskStateError, match="Illegal transition"):
        task.status = TaskStatus.IN_PROGRESS


def test_descriptor_showcase_demonstrates_non_data_priority() -> None:
    demo = DescriptorShowcase()

    assert demo.non_data_label == "shared-label"
    demo.non_data_label = "instance-label"

    assert demo.non_data_label == "instance-label"
    assert DescriptorShowcase.non_data_label == "shared-label"


def test_descriptor_showcase_demonstrates_data_descriptor_priority() -> None:
    demo = DescriptorShowcase()
    demo.protected_text = "updated"
    demo.__dict__["protected_text"] = "shadow"

    assert demo.protected_text == "updated"

    with pytest.raises(TaskValidationError, match="string"):
        demo.protected_text = 10  # type: ignore[assignment]


def test_generated_task_source_returns_expected_tasks() -> None:
    source = GeneratedTaskSource(count=3)

    tasks = list(source.get_tasks())

    assert [task.id for task in tasks] == ["gen-1", "gen-2", "gen-3"]
    assert [task.priority for task in tasks] == [TaskPriority.NORMAL, TaskPriority.NORMAL, TaskPriority.NORMAL]


def test_generated_task_source_with_zero_count_returns_empty_list() -> None:
    source = GeneratedTaskSource(count=0)

    tasks = list(source.get_tasks())

    assert tasks == []


def test_file_task_source_reads_json_and_converts_id_to_string(tmp_path: Path) -> None:
    input_data = [
        {"id": 101, "description": "from file", "priority": "high", "status": "new"},
        {"id": "102", "description": "from file 2", "priority": "low", "status": "in_progress"},
    ]
    data_file = tmp_path / "tasks.json"
    data_file.write_text(json.dumps(input_data), encoding="utf-8")

    source = FileTaskSource(data_file)
    tasks = list(source.get_tasks())

    assert [task.id for task in tasks] == ["101", "102"]
    assert [task.description for task in tasks] == ["from file", "from file 2"]
    assert [task.priority for task in tasks] == [TaskPriority.HIGH, TaskPriority.LOW]
    assert [task.status for task in tasks] == [TaskStatus.NEW, TaskStatus.IN_PROGRESS]


def test_api_stub_source_returns_expected_tasks() -> None:
    source = ApiStubTaskSource()

    tasks = list(source.get_tasks())

    assert [task.id for task in tasks] == ["api-1", "api-2"]
    assert [task.priority for task in tasks] == [TaskPriority.HIGH, TaskPriority.NORMAL]
    assert [task.status for task in tasks] == [TaskStatus.NEW, TaskStatus.IN_PROGRESS]


def test_runtime_protocol_check_accepts_valid_sources() -> None:
    receiver = TaskReceiver()

    for source in (GeneratedTaskSource(1), FileTaskSource("dummy.json"), ApiStubTaskSource()):
        assert isinstance(source, TaskSource)
        receiver.register_source(source)


def test_runtime_protocol_check_rejects_invalid_source() -> None:
    class InvalidSource:
        pass

    receiver = TaskReceiver()

    with pytest.raises(TypeError, match="Source does not satisfy TaskSource contract"):
        receiver.register_source(InvalidSource())  # type: ignore[arg-type]


def test_task_receiver_collects_tasks_from_all_sources_in_registration_order(tmp_path: Path) -> None:
    file_data = [{"id": "file-1", "description": "from file", "priority": "high", "status": "new"}]
    data_file = tmp_path / "tasks.json"
    data_file.write_text(json.dumps(file_data), encoding="utf-8")

    receiver = TaskReceiver()
    receiver.register_source(FileTaskSource(data_file))
    receiver.register_source(GeneratedTaskSource(count=2))
    receiver.register_source(ApiStubTaskSource())

    tasks = receiver.collect_tasks()

    assert [task.id for task in tasks] == ["file-1", "gen-1", "gen-2", "api-1", "api-2"]


def test_main_prints_all_tasks_from_three_sources(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    output_lines = [line.strip() for line in capsys.readouterr().out.splitlines() if line.strip()]

    assert len(output_lines) == 7
    assert output_lines[0].startswith("[file-1] priority=high; status=new; text=first from file")
    assert output_lines[1].startswith("[file-2] priority=low; status=in_progress; text=second from file")
    assert output_lines[2].startswith("[gen-1] priority=normal; status=new; text=Generated task #1")
    assert output_lines[3].startswith("[gen-2] priority=normal; status=new; text=Generated task #2")
    assert output_lines[4].startswith("[gen-3] priority=normal; status=new; text=Generated task #3")
    assert output_lines[5].startswith("[api-1] priority=high; status=new; text=first from api")
    assert output_lines[6].startswith("[api-2] priority=normal; status=in_progress; text=second from api")
