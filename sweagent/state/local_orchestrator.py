import os
import json
import copy
import subprocess
from sweagent.state.snapshot import Snapshot
from typing import List, Dict, Any
from sweagent.state.global_orchestrator import GlobalOrchestrator


class LocalOrchestrator():
    """
    Local Orchestrator tied to an AI agent. Manages agent state, task completion, and snapshot policy.
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.tasks_completed: List[Dict] = []
        self.snapshot_policy = lambda: True  # Placeholder policy, always allows snapshot
        self.snapshots: List[Snapshot] = []

        self.snapshot_dir = f"snapshots/{self.agent_id}"
        os.makedirs(self.snapshot_dir, exist_ok=True)

        # TODO: Create a new fork/working directory for the agent

    def take_system_snapshot(self, container_id, step) -> Dict:
        # Assumes docker container is running
        # docker commit -a "Your Name" <container_id> <image_snapshot_name>
        snapshot_image_name = f"system-snapshot-step-{step}:v1"
        command = [
            "docker",
            "commit",
            container_id, 
            snapshot_image_name
        ]
        process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
        stdout, stderr = process.communicate()
        image_id = stdout.rstrip()

        image_details = {
            "image_name": snapshot_image_name,
            "image_id": image_id
        }
        return image_details

    def get_container_id(self, container_name):
        # docker ps -aqf "name=container_name"
        command = [
            "docker",
            "ps",
            "-aqf", 
            f"name={container_name}"
        ]
        process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
        stdout, stderr = process.communicate()
        container_id = stdout.rstrip()
        return container_id

    def process_system_snapshot(self, system_state, step):
        system_snapshot = copy.deepcopy(system_state)

        container_id = self.get_container_id(system_state["container_name"])
        if not container_id:
            raise RuntimeError(f"Container {system_state['container_name']} not found")
        
        snapshot_image = self.take_system_snapshot(container_id, step)

        system_snapshot["container_id"] = container_id
        system_snapshot["snapshot_image"] = snapshot_image
        return system_snapshot

    def notify_task_completed(self):
        # self.tasks_completed.append()
        self.record_snapshot()

    def can_take_snapshot(self) -> bool:
        return self.snapshot_policy()

    def record_snapshot(self, state, step='FINAL'):
        snapshot = Snapshot()
        # Save agent snapshot
        snapshot.agent_snapshot = state["agent_state"]
        # Save system snapshot
        system_snapshot = self.process_system_snapshot(state["system_state"], step)
        snapshot.system_snapshot = system_snapshot

        self.snapshots.append(snapshot)

        # Save the snapshot to a file
        snapshot_file = f"{self.snapshot_dir}/snapshot_{step}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot.get_snapshot, f, indent=4)
            return snapshot_file

        return None 

    def choose_rollback_snapshot(self):
        # Currently chooses the first snapshot
        # TODO: intelligent model to choose which snapshot to rollback to
        snapshot_files = os.listdir(self.snapshot_dir)
        snapshot_steps = [int(item.split("_")[1].split(".json")[0]) for item in snapshot_files]
        last_snapshot = min(snapshot_steps)

        rollback_snapshot_file = f"{self.snapshot_dir}/snapshot_{last_snapshot}.json"
        return rollback_snapshot_file

    def unpack_snapshot_state(self, snapshot_file):
        with open(snapshot_file, 'r') as f:
            snapshot_json = json.load(f)

        agent_state = snapshot_json["agent_snapshot"]
        system_state = snapshot_json["system_snapshot"]
        return agent_state, system_state

    # def create_docker_container(self, container_name, src_image_id):
    #     port = GlobalOrchestrator.find_free_port()
    #     command = [
    #         "docker",
    #         "run", "--rm", "-p"
    #         f"{port}:8000", 
    #         f"--name={container_name}",
    #         f"{src_image_id}",
    #         "/bin/sh", "-c",
    #         "'/root/python3.11/bin/swerex-remote",
    #         "--auth-token",
    #         "baf17de5-2ae2-40ae-9d10-6d8a95ed7ce4'"
    #     ]
    #      process = subprocess.Popen(command,
    #                                 stdout=subprocess.PIPE,
    #                                 stderr=subprocess.PIPE,
    #                                 text=True)
    #     stdout, stderr = process.communicate()

