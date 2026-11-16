from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tool, User
from app.schemas.tool import ToolCreate, ToolResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/tools",
    tags=["Tools"]
)


# Register a new tool
@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool_data: ToolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_tool = db.query(Tool).filter(
        Tool.name == tool_data.name.strip()
    ).first()

    if existing_tool:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tool already exists"
        )

    new_tool = Tool(
        name=tool_data.name.strip(),
        description=tool_data.description,
        category=tool_data.category,
        is_active=True
    )

    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)

    return new_tool


# Get all registered tools
@router.get("/", response_model=list[ToolResponse])
def get_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tools = db.query(Tool).order_by(Tool.id.asc()).all()

    return tools