# TODO: implement relevant mocks
from datetime import datetime

from google.cloud.tasks_v2 import Task
from pydantic import BaseModel


class CloudTaskClientMock:
    def enqueue(
        self, task_object: BaseModel, schedule_time: datetime = None, name: str = None
    ) -> Task:
        return Task(name="foo")
