
import secrets
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.agent_dependencies import get_current_agent

from app.database import get_db
from app.models import Agent, User
from app.schemas.agent import (
    AgentCreate,
    AgentRegistrationResponse,
    AgentResponse
)

from app.models import Agent, AgentTool, Tool, User

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/agents",
    tags=["Agent Management"]
)


# HASH AGENT API KEY
def hash_agent_key(api_key: str) -> str:
    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


# REGISTER NEW AI AGENT
@router.post(
    "/register",
    response_model=AgentRegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def register_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key = secrets.token_urlsafe(32)

    new_agent = Agent(
    name=agent_data.name.strip(),
    framework=agent_data.framework.strip(),
    description=agent_data.description,
    owner_id=current_user.id,
    credential_hash=hash_agent_key(api_key),
    status="active"
)
    try:
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent registration failed"
        )

    return {
        "id": new_agent.id,
        "name": new_agent.name,
        "framework": new_agent.framework,
        "description": new_agent.description,
        "status": new_agent.status,
        "created_at": new_agent.created_at,
        "agent_api_key": api_key
    }


# GET ALL AGENTS BELONGING TO CURRENT USER
@router.get(
    "/",
    response_model=list[AgentResponse]
)
def get_my_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agents = db.query(Agent).filter(
        Agent.owner_id == current_user.id
    ).all()

    return agents


# GET ONE AGENT
@router.get(
    "/{agent_id}",
    response_model=AgentResponse
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent

@router.get("/auth/verify")
def verify_agent(
    current_agent: Agent = Depends(get_current_agent)
):
    return {
        "message": "Agent authentication successful",
        "agent_id": current_agent.id,
        "name": current_agent.name,
        "framework": current_agent.framework,
        "status": current_agent.status
    }
@router.post("/{agent_id}/rotate-key")
def rotate_agent_key(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the agent belonging to the logged-in user
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Generate a new secret API key
    new_api_key = secrets.token_urlsafe(32)

    # Store only its SHA-256 hash
    agent.credential_hash = hashlib.sha256(
        new_api_key.encode("utf-8")
    ).hexdigest()

    db.commit()
    db.refresh(agent)

    # Return the raw key only once
    return {
        "message": "Agent API key rotated successfully",
        "agent_id": agent.id,
        "agent_api_key": new_api_key
    }
# Assign a tool to an agent
@router.post("/{agent_id}/tools/{tool_id}")
def assign_tool_to_agent(
    agent_id: int,
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the agent belongs to the logged-in user
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Check that the tool exists
    tool = db.query(Tool).filter(
        Tool.id == tool_id
    ).first()

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )

    if not tool.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool is inactive"
        )

    # Check whether the assignment already exists
    existing_assignment = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tool is already assigned to this agent"
        )

    # Create the assignment
    assignment = AgentTool(
    agent_id=agent_id,
    tool_id=tool_id,
    permission="allow"
)

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Tool assigned successfully",
        "agent_id": agent_id,
        "tool_id": tool_id,
        "tool_name": tool.name
    }
# View tools assigned to an agent
@router.get("/{agent_id}/tools")
def get_agent_tools(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    assignments = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id
    ).all()

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "tools": [
            {
                "tool_id": item.tool.id,
                "tool_name": item.tool.name,
                "category": item.tool.category,
                "is_active": item.tool.is_active
            }
            for item in assignments
        ]
    }