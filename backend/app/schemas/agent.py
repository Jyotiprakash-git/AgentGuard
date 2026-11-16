
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AgentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    framework: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(
        default=None,
        max_length=2000
    )


class AgentRegistrationResponse(BaseModel):
    id: int
    name: str
    framework: str
    description: Optional[str]
    status: str
    created_at: datetime
    agent_api_key: str


class AgentResponse(BaseModel):
    id: int
    name: str
    framework: str
    description: Optional[str]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
