import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Set
import copy

from .models import ResourceRequirements, Job


# =============
# Merkle Tree (Unchanged)
# =============
class MerkleTree:
    def __init__(self):
        self.root = None
        self.leaves = []

    def build(self, data: List[str]):
        """Builds a Merkle tree from serialized job data"""
        if not data:
            return ""

        # Pad to even number of leaves
        if len(data) % 2 != 0:
            data.append(data[-1])

        self.leaves = [self._hash(d) for d in data]
        self.root = self._build_tree(self.leaves)
        return self.root.hash

    def _build_tree(self, nodes: List[str]):
        if len(nodes) == 1:
            return Node(nodes[0])

        new_level = []
        for i in range(0, len(nodes) - 1, 2):
            combined = nodes[i] + nodes[i + 1]
            new_node = Node(self._hash(combined))
            new_node.left = Node(nodes[i])
            new_node.right = Node(nodes[i + 1])
            new_level.append(new_node.hash)

        return self._build_tree(new_level)

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()


class Node:
    def __init__(self, hash_val: str):
        self.hash = hash_val
        self.left = None
        self.right = None


# =================
# Job Manager System (Refactored)
# =================
class JobManager:
    def __init__(self):
        self.active_jobs: Dict[str, Job] = {}
        self.job_history: List[Job] = []
        self.merkle_tree = MerkleTree()
        self.current_root_hash: Optional[str] = None
        self._update_merkle_root()

    def create_job(
        self,
        job_id: str,
        priority: int,
        user_id: str,
        resources: ResourceRequirements,
        command: str,
    ) -> Job:
        """Create a new job with dynamic resource requirements"""
        if job_id in self.active_jobs:
            raise ValueError(f"Job {job_id} already exists")

        job = Job(job_id, priority, user_id, resources, command)
        self.active_jobs[job_id] = job
        self._update_merkle_root()
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.active_jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        return list(self.active_jobs.values())

    def update_job(self, job_id: str, **kwargs) -> Job:
        """Update job attributes, including dynamic resource requirements"""
        if job_id not in self.active_jobs:
            raise KeyError(f"Job {job_id} not found")

        job = self.active_jobs[job_id]
        
        if 'resources' in kwargs:
            if not isinstance(kwargs['resources'], ResourceRequirements):
                raise ValueError("Resources must be a ResourceRequirements object")
            job.resources = kwargs.pop('resources')
        
        # Update other attributes
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)

        self._update_merkle_root()
        return job

    def delete_job(self, job_id: str) -> None:
        if job_id not in self.active_jobs:
            raise KeyError(f"Job {job_id} not found")

        self.job_history.append(self.active_jobs[job_id])
        del self.active_jobs[job_id]
        self._update_merkle_root()

    def verify_integrity(self) -> bool:
        """Verify current jobs match the stored Merkle root"""
        current_data = [job.serialize() for job in self.active_jobs.values()]
        temp_tree = MerkleTree()
        new_root = temp_tree.build(current_data)
        return new_root == self.current_root_hash

    def compare_states(self, other_manager: "JobManager") -> Dict:
        """Compare two job managers and identify differences"""
        result = {
            "root_match": self.current_root_hash == other_manager.current_root_hash,
            "jobs_added": [],
            "jobs_removed": [],
            "jobs_modified": [],
        }

        our_jobs = set(self.active_jobs.keys())
        their_jobs = set(other_manager.active_jobs.keys())

        result["jobs_added"] = list(their_jobs - our_jobs)
        result["jobs_removed"] = list(our_jobs - their_jobs)

        common_jobs = our_jobs & their_jobs
        for job_id in common_jobs:
            if (
                self.active_jobs[job_id].serialize()
                != other_manager.active_jobs[job_id].serialize()
            ):
                result["jobs_modified"].append(job_id)

        return result

    def _update_merkle_root(self) -> None:
        """Internal method to update the Merkle root when jobs change"""
        current_data = [job.serialize() for job in self.active_jobs.values()]
        self.current_root_hash = self.merkle_tree.build(current_data)

    def get_merkle_proof(self, job_id: str) -> Optional[List[str]]:
        """Get Merkle proof for a specific job"""
        if job_id not in self.active_jobs:
            return None

        target_hash = self._hash_job(self.active_jobs[job_id])
        return self._generate_proof(target_hash, self.merkle_tree.leaves)

    def _hash_job(self, job: Job) -> str:
        return self.merkle_tree._hash(job.serialize())

    def _generate_proof(self, target_hash: str, leaves: List[str]) -> List[str]:
        """Generate Merkle proof for a leaf node"""
        proof = []
        index = leaves.index(target_hash)

        while len(leaves) > 1:
            if index % 2 == 1:
                proof.append(leaves[index - 1])
            else:
                if index + 1 < len(leaves):
                    proof.append(leaves[index + 1])

            # Move up one level
            index = index // 2
            leaves = [
                self.merkle_tree._hash(leaves[i] + leaves[i + 1])
                for i in range(0, len(leaves) - 1, 2)
            ]

        return proof


# ==============
# Test (Updated)
# ==============
if __name__ == "__main__":
    # Initialize two managers
    manager1 = JobManager()
    manager2 = JobManager()

    # Create jobs in manager1 with dynamic resources
    manager1.create_job(
        "J1", 
        1, 
        "user1", 
        ResourceRequirements(cpu_cores=4, memory_gb=8.0), 
        "python script1.py"
    )
    manager1.create_job(
        "J2", 
        2, 
        "user2", 
        ResourceRequirements(cpu_cores=2, memory_gb=4.0, gpu_units=1), 
        "python script2.py"
    )

    # Clone manager1 to manager2
    manager2.active_jobs = copy.deepcopy(manager1.active_jobs)
    manager2._update_merkle_root()

    # Modify a job in manager2 with new resource structure
    new_resources = ResourceRequirements(cpu_cores=8, memory_gb=16.0)
    manager2.update_job("J1", priority=3, resources=new_resources)

    # Compare states
    diff = manager1.compare_states(manager2)
    print("System Differences:")
    print(f"- Root hashes match: {diff['root_match']}")
    print(f"- Modified jobs: {diff['jobs_modified']}")

    # Verification
    print("\nManager1 Integrity:", manager1.verify_integrity())
    print("Manager2 Integrity:", manager2.verify_integrity())