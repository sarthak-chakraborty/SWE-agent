from fastapi import FastAPI, HTTPException, status
import uvicorn
import socket
import subprocess
from pydantic import BaseModel
from sweagent.state.models import (
    StartTaskRequest,
    StartTaskResponse
)

app = FastAPI(
    title="Global Orchestrator Service"
)

class GlobalOrchestrator:
    """
    Global Orchestrator that starts a LocalOrchestrator when a user prompts the agent to do a task.
    """
    def __init__(self):
        self.running_local_orchestrators = {}

    @classmethod
    def find_free_port(cls):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))  # Bind to a free port provided by the OS
            return s.getsockname()[1]

    def handle_merging(self, *args, **kwargs):
        pass


global_orchestrator = GlobalOrchestrator()
HOST = "127.0.0.1"

@app.post("/start_task", response_model=StartTaskResponse)
def start_local_orchestrator(request: StartTaskRequest):
    agent_id = request.agent_id
    try:
        if agent_id in global_orchestrator.running_local_orchestrators:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Local Orchestrator for '{agent_id}' alredy exists"
            )

        port = GlobalOrchestrator.find_free_port()

        command = [
            "python",
            "local_orchestrator_service.py",
            "--agent-id", agent_id,
            "--port", str(port)
        ]

        process = subprocess.Popen(command)

        global_orchestrator.running_local_orchestrators[agent_id] = {"process": process, "port": port, "host": HOST}

        return StartTaskResponse(
            status="success",
            message="Local Orchestrator spawned successfully",
            local_orchestrator_url=f"http://{HOST}:{port}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)