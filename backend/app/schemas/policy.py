
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any


class PolicyEvaluateRequest(BaseModel):
    action: str
    resource: str
    request_data: Optional[Dict[str, Any]] = None

class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    action: str
    resource: Optional[str] = None
    effect: str
    conditions: Optional[Dict[str, Any]] = None
    is_enabled: bool = True


class PolicyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    agent_id: Optional[int] = None
    action: str
    resource: Optional[str] = None
    effect: str
    conditions: Optional[Dict[str, Any]] = None
    is_enabled: bool

    model_config = ConfigDict(from_attributes=True)
