from datetime import datetime


# ===================
# Core Data Structures
# ===================
class ResourceRequirements:
    def __init__(self, cpu_cores: int, memory_gb: float, gpu_units: int = 0):
        self.cpu_cores = cpu_cores
        self.memory_gb = memory_gb
        self.gpu_units = gpu_units


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
        return (
            f"{self.id}|{self.priority}|{self.user_id}|"
            f"{self.resources.cpu_cores}|{self.resources.memory_gb}|"
            f"{self.resources.gpu_units}|{self.command}|"
            f"{self.submission_time.timestamp()}"
        )
