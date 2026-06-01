import json
import logging
import tempfile
from pathlib import Path

from src.logging_config import setup_logging
from src.task_receiver import TaskReceiver
from src.sources.api_stub_source import ApiStubTaskSource
from src.sources.file_source import FileTaskSource
from src.sources.generator_source import GeneratedTaskSource


def main() -> None:
    log_path = Path(__file__).resolve().parent.parent / "shell.log"
    setup_logging(log_path)
    logger = logging.getLogger(__name__)

    file_payload = [
        {
            "id": "file-1",
            "description": "first from file",
            "priority": "high",
            "status": "new",
        },
        {
            "id": "file-2",
            "description": "second from file",
            "priority": "low",
            "status": "in_progress",
        },
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = Path(tmp_dir) / "tasks.json"
        tmp_file_path.write_text(json.dumps(file_payload, ensure_ascii=False), encoding="utf-8")
        logger.info("Создан временный JSON-файл с задачами: %s", tmp_file_path)

        receiver = TaskReceiver()
        receiver.register_source(FileTaskSource(tmp_file_path))
        receiver.register_source(GeneratedTaskSource(count=3))
        receiver.register_source(ApiStubTaskSource())

        tasks = receiver.collect_tasks()
        logger.info("Собрано задач: %s", len(tasks))

        for task in tasks:
            print(
                f"[{task.id}] priority={task.priority.value}; "
                f"status={task.status.value}; text={task.description}"
            )
            logger.info("Выведена задача id=%s", task.id)

if __name__ == "__main__":
    main()
