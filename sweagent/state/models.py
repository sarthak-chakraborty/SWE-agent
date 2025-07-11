from pydantic import BaseModel
from typing import Dict, Any
from sweagent.types import StepOutput

class StartTaskRequest(BaseModel):
    agent_id: str

class StartTaskResponse(BaseModel):
    status: str
    message: str
    local_orchestrator_url: str

class SnapshotInitiationRequest(BaseModel):
    step: int
    step_output: StepOutput

class SnapshotInitiationResponse(BaseModel):
    initiate: bool
    message: str
    
class NotifyRequest(BaseModel):
    state: Dict[str, Any]
    step: int

class NotifyResponse(BaseModel):
    message: str

class SnapshotRollbackResponse(BaseModel):
    agent_state: Dict[str, Any]
    system_state: Dict[str, Any]
    message: str

class SetSystemStateRequest(BaseModel):
    state: Dict[str, Any]