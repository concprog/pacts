# run.py

import unittest
from pacts.merkleblock import JobManager, MerkleTree
from pacts.models import Job, ResourceRequirements
from pacts.scheduler import Scheduler

class TestMerkleTree(unittest.TestCase):
    def test_build(self):
        merkle_tree = MerkleTree()
        data = ["job1", "job2", "job3"]
        root_hash = merkle_tree.build(data)
        self.assertIsNotNone(root_hash)

    def test_hash(self):
        merkle_tree = MerkleTree()
        data = "job1"
        hash_value = merkle_tree._hash(data)
        self.assertIsNotNone(hash_value)

class TestJobManager(unittest.TestCase):
    def test_create_job(self):
        job_manager = JobManager()
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)

        command = "python script1.py"
        job = job_manager.create_job(job_id, priority, user_id, resources, command)
        self.assertIsNotNone(job)

    def test_get_job(self):
        job_manager = JobManager()
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        job_manager.create_job(job_id, priority, user_id, resources, command)
        job = job_manager.get_job(job_id)
        self.assertIsNotNone(job)

    def test_update_job(self):
        job_manager = JobManager()
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        job_manager.create_job(job_id, priority, user_id, resources, command)
        new_priority = 2
        job_manager.update_job(job_id, priority=new_priority)
        job = job_manager.get_job(job_id)
        self.assertEqual(job.priority, new_priority)

    def test_delete_job(self):
        job_manager = JobManager()
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        job_manager.create_job(job_id, priority, user_id, resources, command)
        job_manager.delete_job(job_id)
        job = job_manager.get_job(job_id)
        self.assertIsNone(job)

class TestScheduler(unittest.TestCase):
    def test_add_job(self):
        scheduler = Scheduler(ResourceRequirements(cpu_cores=8, memory_gb=16.0))
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        job = Job(job_id, priority, user_id, resources, command)
        scheduler.add_job(job)
        self.assertIn(job_id, scheduler.job_queue.queue)

    def test_schedule_jobs(self):
        scheduler = Scheduler(ResourceRequirements(cpu_cores=8, memory_gb=16.0))
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        scheduler.add_job(Job(job_id, priority, user_id, resources, command))
        scheduler.schedule_jobs()
        self.assertIn(job_id, scheduler.scheduled_jobs)

    def test_complete_job(self):
        scheduler = Scheduler(ResourceRequirements(cpu_cores=8, memory_gb=16.0))
        job_id = "job1"
        priority = 1
        user_id = "user1"
        resources = ResourceRequirements(cpu_cores=4, memory_gb=8.0)
        command = "python script1.py"
        scheduler.add_job(Job(job_id, priority, user_id, resources, command))
        scheduler.schedule_jobs()
        scheduler.complete_job(job_id)
        self.assertEqual(scheduler.get_resource_status(), "completed")

if __name__ == "__main__":
    unittest.main()
