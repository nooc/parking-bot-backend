from datetime import datetime

from google.cloud.tasks_v2 import CloudTasksClient, HttpMethod, Task
from google.protobuf import timestamp_pb2
from pydantic import BaseModel

from app.config import Settings
from app.util import http_error as err


class TaskManager:
    def __init__(self, client: CloudTasksClient, cfg: Settings) -> None:
        self.parent = client.queue_path(
            cfg.GOOGLE_CLOUD_PROJECT, cfg.GAE_REGION, cfg.TASK_QUEUE_NAME
        )
        self._client = client

    def enqueue(
        self, task_object: BaseModel, schedule_time: datetime = None, name: str = None
    ) -> Task:
        task = {
            "app_engine_http_request": {
                "http_method": HttpMethod.POST,
                "relative_uri": "/tasks",
            },
            "app_engine_http_request": {
                "headers": {"Content-type": "application/json"},
                "body": task_object.model_dump_json().encode(),
            },
        }
        if name:
            task["name"] = name
        if schedule_time:
            # App schedule time as a protobuf timestamp
            st_pb = timestamp_pb2.Timestamp()
            st_pb.FromDatetime(schedule_time)
            task["schedule_time"] = st_pb

        # File the task
        response = client.create_task(parent=self.parent, task=task)
        return response or err.internal(f"Could not create task {name}.")
