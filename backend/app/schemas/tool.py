from pydantic import BaseModel, ConfigDict
from typing import Optional


class ToolCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class ToolResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)