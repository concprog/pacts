from queue import PriorityQueue
from typing import List, Dict, Set
from .models import Job, ResourceRequirements

class Scheduler:
    def __init__(self, total_resources: ResourceRequirements):
        self.total_resources = total_resources
        self.available_resources = total_resources.copy()
        self.job_queue = PriorityQueue()
        self.scheduled_jobs: Dict[str, Job] = {}
        self.resource_types: Set[str] = set(total_resources.store.keys())
    
    def test(self, job: Job) -> bool:
        """Check if a job can be scheduled given available resources."""
        for resource in self.resource_types:
            if hasattr(job.resources, resource):
                if getattr(job.resources, resource) > getattr(self.available_resources, resource):
                    return False
        return True
    
    def add_job(self, job: Job):
        """Adds a job to the priority queue."""
        self.job_queue.put((-job.priority, job))  # Higher priority = lower value
    
    def allocate_resources(self, job: Job):
        """Allocates resources for a scheduled job."""
        for resource in self.resource_types:
            if hasattr(job.resources, resource):
                current = getattr(self.available_resources, resource)
                setattr(self.available_resources, resource, current - getattr(job.resources, resource))
    
    def release_resources(self, job: Job):
        """Releases resources when a job is completed."""
        for resource in self.resource_types:
            if hasattr(job.resources, resource):
                current = getattr(self.available_resources, resource)
                setattr(self.available_resources, resource, current + getattr(job.resources, resource))
    
    def schedule_jobs(self):
        """Schedules jobs based on priority and resource availability."""
        temp_queue = PriorityQueue()
        
        while not self.job_queue.empty():
            _, job = self.job_queue.get()
            if self.test(job):
                self.allocate_resources(job)
                job.status = "running"
                self.scheduled_jobs[job.id] = job
                print(f"Scheduled Job {job.id} (Priority: {job.priority})")
            else:
                temp_queue.put((-job.priority, job))
        
        # Put unscheduled jobs back in the queue
        while not temp_queue.empty():
            self.job_queue.put(temp_queue.get())
    
    def complete_job(self, job_id: str):
        """Marks a job as completed and releases resources."""
        if job_id in self.scheduled_jobs:
            job = self.scheduled_jobs.pop(job_id)
            job.status = "completed"
            self.release_resources(job)
            print(f"Job {job_id} completed and resources released.")
        else:
            print(f"Job {job_id} not found in scheduled jobs.")
    
    def get_resource_status(self) -> Dict[str, Dict[str, float]]:
        """Returns current resource allocation status."""
        return {
            'total': self.total_resources.store,
            'available': self.available_resources.store,
            'used': {
                k: self.total_resources.store[k] - self.available_resources.store[k]
                for k in self.resource_types
            }
        }

# Example Usage
if __name__ == "__main__":
    system_resources = ResourceRequirements(cpu_cores=8, memory_gb=16.0, gpu_units=1)
    scheduler = Scheduler(system_resources)
    
    # Creating jobs
    job1 = Job("J1", priority=3, user_id="user1", 
              resources=ResourceRequirements(cpu_cores=4, memory_gb=8.0), 
              command="run task 1")
    job2 = Job("J2", priority=1, user_id="user2", 
              resources=ResourceRequirements(cpu_cores=2, memory_gb=4.0), 
              command="run task 2")
    job3 = Job("J3", priority=2, user_id="user3", 
              resources=ResourceRequirements(cpu_cores=4, memory_gb=10.0), 
              command="run task 3")
    
    # Adding jobs to the scheduler
    scheduler.add_job(job1)
    scheduler.add_job(job2)
    scheduler.add_job(job3)
    
    # Performing scheduling
    scheduler.schedule_jobs()
    print("Resource Status:", scheduler.get_resource_status())
    
    # Completing a job
    scheduler.complete_job("J1")
    print("Resource Status after completion:", scheduler.get_resource_status())
    
    # Re-attempting scheduling
    scheduler.schedule_jobs()
    print("Final Resource Status:", scheduler.get_resource_status())