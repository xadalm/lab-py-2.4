import logging

from src.task import Task
from src.task_queue import TaskQueue
from src.task_source import TaskSource


logger = logging.getLogger(__name__)


class TaskReceiver:
    def __init__(self) -> None:
        self._sources: list[TaskSource] = []

    def register_source(self, source: TaskSource) -> None:
        if not isinstance(source, TaskSource):
            logger.error("Попытка зарегистрировать источник без контракта: %s", type(source).__name__)
            raise TypeError("Source does not satisfy TaskSource contract")
        self._sources.append(source)
        logger.info("Зарегистрирован источник: %s", type(source).__name__)

    def collect_tasks(self) -> TaskQueue:
        collected = TaskQueue()
        for source in self._sources:
            source_tasks = list(source.get_tasks())
            collected.extend_tasks(source_tasks)
            logger.info("Источник %s вернул задач: %s", type(source).__name__, len(source_tasks))
        logger.info("Всего собрано задач: %s", len(collected))
        return collected