
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict


class ApprovalReviewRequest(BaseModel):
    reason: Optional[str] = None


class ApprovalRequestResponse(BaseModel):
    id: int
    agent_id: int
    requested_by_user_id: Optional[int] = None
    approved_by_user_id: Optional[int] = None
    action: str
    request_data: Optional[Dict[str, Any]] = None
    status: str
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
