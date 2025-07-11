from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import argparse
import uvicorn
from sweagent.state.local_orchestrator import LocalOrchestrator
from sweagent.state.oracle import Oracle
from sweagent.types import StepOutput
from sweagent.state.models import (
    SnapshotInitiationRequest,
    SnapshotInitiationResponse,
    NotifyRequest,
    NotifyResponse,
    SnapshotRollbackResponse,
    SetSystemStateRequest
)


def run_service(agent_id, port):
    app = FastAPI(
        title="Local Orchestrator Service"
    )

    local_orchestrator = LocalOrchestrator(agent_id=agent_id)

    @app.post("/initiate_snapshot", response_model=SnapshotInitiationResponse)
    def request_snapshot(request: SnapshotInitiationRequest):
        step_verification = Oracle.verify_step(request.step_output, request.step)
        if not step_verification:
            message = "Step Verification Failed. Rollback!!"
            return SnapshotInitiationResponse(initiate=False, message=message)
            
        initiate_snapshot = local_orchestrator.can_take_snapshot()
        message = "Initiate Snapshot" if initiate_snapshot else "Snapshot not required"
        return SnapshotInitiationResponse(initiate=initiate_snapshot, message=message)

    @app.post("/notify_snapshot", response_model=NotifyResponse)
    def notify_snapshot(request: NotifyRequest):
        return_val = local_orchestrator.record_snapshot(
            state=request.state,
            step=request.step
        )
        if not return_val:
            raise HTTPException(status_code=500, detail=str(e))
        
        return NotifyResponse(message="Snapshot received and saved")

    @app.post("/choose_rollback_snapshot", response_model=SnapshotRollbackResponse)
    def choose_rollback_snapshot():
        rollback_snapshot_file = local_orchestrator.choose_rollback_snapshot()
        agent_state, system_state = local_orchestrator.unpack_snapshot_state(rollback_snapshot_file)

        return SnapshotRollbackResponse(agent_state=agent_state, 
                                        system_state=system_state, 
                                        message=f"Rollback Snapshot chosen: {rollback_snapshot_file}")

    # @app.post("/set_system_state")
    # def set_system_state(request: SetSystemStateRequest):
    #     state = request.state
    #     local_orchestrator.create_docker_container(container_name=state["container_name"],
    #                                                src_image_id=state["snapshot_image"]["image_id"])
        

    print(f"-- Starting Local Orchestrator for Agent {agent_id} on port {port} --")
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True, type=str)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    
    run_service(agent_id=args.agent_id, port=args.port)