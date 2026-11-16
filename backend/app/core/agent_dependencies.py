
import hashlib

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent


def get_current_agent(
    agent_api_key: str | None = Header(
        default=None,
        alias="X-Agent-API-Key"
    ),
    db: Session = Depends(get_db)
) -> Agent:

    if not agent_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent API key is required"
        )

    hashed_key = hashlib.sha256(
        agent_api_key.encode("utf-8")
    ).hexdigest()

    agent = db.query(Agent).filter(
        Agent.credential_hash == hashed_key
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent API key"
        )

    if agent.status.lower() != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent is inactive"
        )

    return agent
