from datetime import datetime
from typing import Any

class ResourceRequirements:
    def __init__(self, **kwargs):
        self.store = kwargs or {}

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'store':
            super().__setattr__(name, value)
        else:
            self.store[name] = value

    def __getattr__(self, name):
        try:
            return self.store[name]
        except KeyError as e:
            raise AttributeError(f"'ResourceRequirements' has no resource '{name}'") from e

    def copy(self):
        return ResourceRequirements(**self.store)

    def serialize(self) -> str:
        return ",".join([f"{key}:{value}" for key, value in sorted(self.store.items())])


class Job:
    def __init__(
        self,
        job_id: str,
        priority: int,
        user_id: str,
        resources: ResourceRequirements,
        command: str,
    ):
        self.id = job_id
        self.priority = priority
        self.user_id = user_id
        self.resources = resources
        self.command = command
        self.submission_time = datetime.now()
        self.status = "queued"  # queued/running/completed/failed

    def serialize(self) -> str:
        # Get all resource requirements dynamically from the store
        
        return (
            f"{self.id}|{self.priority}|{self.user_id}|"
            f"{self.resources.serialize()}|{self.command}|"
            f"{self.submission_time.timestamp()}"
        )