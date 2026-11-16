
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agents = relationship("Agent", back_populates="owner")


# 2. AGENTS TABLE
class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    framework = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    credential_hash = Column(String(255), nullable=True, unique=True)

    status = Column(String(50), default="active")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="agents")
    agent_tools = relationship("AgentTool", back_populates="agent")
    approval_requests = relationship("ApprovalRequest", back_populates="agent")
    audit_logs = relationship("AuditLog", back_populates="agent")


# 3. TOOLS TABLE
class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    agent_tools = relationship("AgentTool", back_populates="tool")



# 4. AGENT_TOOLS TABLE
class AgentTool(Base):
    __tablename__ = "agent_tools"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)

    permission = Column(String(50), nullable=False, default="allow")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("agent_id", "tool_id", name="uq_agent_tool"),
    )

    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")



# 5. SECURITY_POLICIES TABLE
class SecurityPolicy(Base):
    __tablename__ = "security_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=True
    )

    effect = Column(String(20), default="deny", nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(150), nullable=True)
    conditions = Column(JSON, nullable=True)

    is_enabled = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )



# 6. APPROVAL_REQUESTS TABLE
class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False
    )

    requested_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    approved_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    action = Column(String(150), nullable=False)

    request_data = Column(JSON, nullable=True)

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    reason = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    agent = relationship(
        "Agent",
        back_populates="approval_requests"
    )


# 7. AUDIT_LOGS TABLE
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    event_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=True)
    decision = Column(String, nullable=False)

    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    agent = relationship("Agent", back_populates="audit_logs")

# 8. TOOL_EXECUTIONS TABLE
class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(Integer, primary_key=True, index=True)

    # One execution record per approval request
    approval_request_id = Column(
        Integer,
        ForeignKey("approval_requests.id"),
        nullable=False,
        unique=True
    )

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False
    )

    tool_id = Column(
        Integer,
        ForeignKey("tools.id"),
        nullable=False
    )

    status = Column(
        String(30),
        default="started",
        nullable=False
    )

    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
