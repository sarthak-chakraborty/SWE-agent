import uuid 
from typing import Dict, Any

class Snapshot:
    """
    A class to represent a snapshot.
    """
    def __init__(self):
        self._id = str(uuid.uuid4())
        self.agent_snapshot: Dict[str, Any] = {}
        self.system_snapshot: Dict[str, Any] = {}

    @property
    def get_id(self) -> str:
        """
        Returns the unique identifier of the snapshot.
        """
        return self._id
    
    @property
    def get_snapshot(self) -> Dict[str, Any]:
        """
        Returns the snapshot as a dictionary.
        """
        return {
            "id": self._id,
            "agent_snapshot": self.agent_snapshot,
            "system_snapshot": self.system_snapshot
        }

    
