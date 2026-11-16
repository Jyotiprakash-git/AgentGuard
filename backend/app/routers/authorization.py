import re
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import (
    Agent,
    AgentTool,
    Tool,
    SecurityPolicy,
    AuditLog,
    ApprovalRequest,
    ToolExecution
)
from app.models import User
from app.core.agent_dependencies import get_current_agent
from app.core.dependencies import get_current_user
from app.schemas.policy import (
    PolicyEvaluateRequest,
    PolicyCreate,
    PolicyResponse
)
from datetime import datetime, timezone

from app.schemas.approval import (
    ApprovalReviewRequest,
    ApprovalRequestResponse
)
router = APIRouter(
    prefix="/authorization",
    tags=["Authorization"]
)


@router.post("/check-tool/{tool_id}")
def check_tool_permission(
    tool_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # Step 1: Check whether the tool exists and is active
    tool = db.query(Tool).filter(
        Tool.id == tool_id,
        Tool.is_active == True
    ).first()

    if not tool:
        raise HTTPException(
            status_code=404,
            detail="Tool not found or inactive"
        )

    # Step 2: Check whether this tool is assigned to the agent
    assignment = db.query(AgentTool).filter(
        AgentTool.agent_id == agent.id,
        AgentTool.tool_id == tool_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="Agent is not authorized to use this tool"
        )

    # Step 3: Check the assigned permission
    if assignment.permission.lower() != "allow":
        raise HTTPException(
            status_code=403,
            detail="Tool access denied by AgentGuard"
        )

    # Step 4: Return authorization result
    return {
        "authorized": True,
        "decision": "ALLOW",
        "agent_id": agent.id,
        "agent_name": agent.name,
        "tool_id": tool.id,
        "tool_name": tool.name,
        "permission": assignment.permission,
        "message": "Agent is authorized to use this tool"
    }

@router.post("/evaluate")
def evaluate_policy(
    payload: PolicyEvaluateRequest,
    request: Request,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    policies = db.query(SecurityPolicy).filter(
        SecurityPolicy.agent_id == agent.id,
        SecurityPolicy.is_enabled == True
    ).all()

    # Find policies matching the requested action and resource
    matching_policies = [
        policy for policy in policies
        if (
            policy.action.lower() in [payload.action.lower(), "*"]
            and (
                policy.resource is None
                or policy.resource.lower() in [
                    payload.resource.lower(), "*"
                ]
            )
        )
    ]

    decision = "DENY"
    reason = "No matching allow policy found"
    approval_request_id = None

    deny_policy = next(
        (p for p in matching_policies if p.effect.lower() == "deny"),
        None
    )

    approval_policy = next(
        (
            p for p in matching_policies
            if p.effect.lower() == "require_approval"
        ),
        None
    )

    allow_policy = next(
        (p for p in matching_policies if p.effect.lower() == "allow"),
        None
    )

    # DENY has the highest priority
    if deny_policy:
        decision = "DENY"
        reason = f"Blocked by policy: {deny_policy.name}"

    # Human approval is required
    elif approval_policy:
        decision = "REQUIRE_APPROVAL"
        reason = f"Human approval required by policy: {approval_policy.name}"

        approval_entry = ApprovalRequest(
            agent_id=agent.id,
            requested_by_user_id=agent.owner_id,
            action=payload.action,
            request_data={
                "resource": payload.resource,
                **(payload.request_data or {})
            },
            status="pending",
            reason=reason
        )

        db.add(approval_entry)
        db.flush()

        approval_request_id = approval_entry.id

    # ALLOW if an allow policy matches
    elif allow_policy:
        decision = "ALLOW"
        reason = f"Allowed by policy: {allow_policy.name}"

    # Record the evaluation in the audit log
    ip_address = request.client.host if request.client else None

    audit_entry = AuditLog(
        agent_id=agent.id,
        user_id=agent.owner_id,
        event_type="POLICY_EVALUATION",
        action=payload.action,
        resource=payload.resource,
        decision=decision,
        details={
            "reason": reason,
            "approval_request_id": approval_request_id
        },
        ip_address=ip_address
    )

    db.add(audit_entry)
    db.commit()

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "action": payload.action,
        "resource": payload.resource,
        "decision": decision,
        "reason": reason,
        "approval_request_id": approval_request_id
    }



@router.post("/policies/{agent_id}", response_model=PolicyResponse)
def create_policy(
    agent_id: int,
    policy_data: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check whether the agent belongs to the logged-in user
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or access denied"
        )

    # Validate the policy effect
    effect = policy_data.effect.lower()

    if effect not in ["allow", "deny","require_approval"]:
        raise HTTPException(
            status_code=400,
            detail="Effect must be either allow or deny"
        )

    # Create the policy
    new_policy = SecurityPolicy(
        name=policy_data.name,
        description=policy_data.description,
        agent_id=agent.id,
        action=policy_data.action,
        resource=policy_data.resource,
        effect=effect,
        conditions=policy_data.conditions,
        is_enabled=policy_data.is_enabled
    )

    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    return new_policy

@router.get("/policies/{agent_id}", response_model=list[PolicyResponse])
def get_agent_policies(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify agent ownership
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or access denied"
        )

    # Return policies belonging to this agent
    policies = db.query(SecurityPolicy).filter(
        SecurityPolicy.agent_id == agent.id
    ).order_by(SecurityPolicy.id.desc()).all()

    return policies

@router.get("/audit-logs/{agent_id}")
def get_agent_audit_logs(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verify that the agent belongs to the logged-in user
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or access denied"
        )

    # 2. Fetch audit logs for this agent
    logs = db.query(AuditLog).filter(
        AuditLog.agent_id == agent.id
    ).order_by(AuditLog.id.desc()).all()

    # 3. Return the logs
    return [
        {
            "id": log.id,
            "agent_id": log.agent_id,
            "user_id": log.user_id,
            "event_type": log.event_type,
            "action": log.action,
            "resource": log.resource,
            "decision": log.decision,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        for log in logs
    ]

@router.post("/approval-requests")
def create_approval_request(
    payload: dict,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # 1. Get and validate the requested action
    action = payload.get("action")

    if not isinstance(action, str) or not action.strip():
        raise HTTPException(
            status_code=400,
            detail="Action is required"
        )

    # 2. Get additional request information
    request_data = payload.get("request_data")

    if request_data is not None and not isinstance(request_data, dict):
        raise HTTPException(
            status_code=400,
            detail="request_data must be a JSON object"
        )

    # 3. Create the approval request
    new_request = ApprovalRequest(
        agent_id=agent.id,
        requested_by_user_id=agent.owner_id,
        action=action.strip(),
        request_data=request_data,
        status="pending",
        reason=payload.get("reason")
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # 4. Return the created request
    return {
        "message": "Approval request created successfully",
        "approval_request": {
            "id": new_request.id,
            "agent_id": new_request.agent_id,
            "requested_by_user_id": new_request.requested_by_user_id,
            "action": new_request.action,
            "request_data": new_request.request_data,
            "status": new_request.status,
            "reason": new_request.reason,
            "created_at": new_request.created_at
        }
    }

# 1. VIEW APPROVAL REQUESTS
@router.get(
    "/approval-requests",
    response_model=list[ApprovalRequestResponse]
)
def get_approval_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = (
        db.query(ApprovalRequest)
        .join(Agent, ApprovalRequest.agent_id == Agent.id)
        .filter(Agent.owner_id == current_user.id)
        .order_by(ApprovalRequest.id.desc())
        .all()
    )

    return requests


# 2. APPROVE AN APPROVAL REQUEST
@router.post(
    "/approval-requests/{request_id}/approve",
    response_model=ApprovalRequestResponse
)
def approve_request(
    request_id: int,
    review_data: ApprovalReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    approval = (
        db.query(ApprovalRequest)
        .join(Agent, ApprovalRequest.agent_id == Agent.id)
        .filter(
            ApprovalRequest.id == request_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found or access denied"
        )

    if approval.status.lower() != "pending":
        raise HTTPException(
            status_code=400,
            detail="This request has already been reviewed"
        )

    approval.status = "approved"
    approval.approved_by_user_id = current_user.id
    approval.reviewed_at = datetime.now(timezone.utc)

    if review_data.reason:
        approval.reason = review_data.reason

    db.commit()
    db.refresh(approval)

    return approval


# 3. REJECT AN APPROVAL REQUEST
@router.post(
    "/approval-requests/{request_id}/reject",
    response_model=ApprovalRequestResponse
)
def reject_request(
    request_id: int,
    review_data: ApprovalReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Find the approval request and verify ownership
    approval = (
        db.query(ApprovalRequest)
        .join(Agent, ApprovalRequest.agent_id == Agent.id)
        .filter(
            ApprovalRequest.id == request_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found or access denied"
        )

    # 2. Only pending requests can be rejected
    if approval.status.lower() != "pending":
        raise HTTPException(
            status_code=400,
            detail="This request has already been reviewed"
        )

    # 3. Update approval status
    approval.status = "rejected"
    approval.approved_by_user_id = current_user.id
    approval.reviewed_at = datetime.now(timezone.utc)

    if review_data.reason:
        approval.reason = review_data.reason

    # 4. Create audit log
    audit_entry = AuditLog(
        agent_id=approval.agent_id,
        user_id=current_user.id,
        event_type="APPROVAL_REJECTED",
        action=approval.action,
        resource=(approval.request_data or {}).get("resource"),
        decision="REJECTED",
        details={
            "approval_request_id": approval.id,
            "reason": approval.reason,
            "rejected_by_user_id": current_user.id
        }
    )

    db.add(audit_entry)

    # 5. Save both changes
    db.commit()
    db.refresh(approval)

    return approval

# SAFE EMAIL EXECUTION - TEST MODE
def simulate_email_send(recipient: str, subject: str, body: str):
    """
    Simulates email delivery.
    Does NOT send an actual email.
    """

    return {
        "execution_mode": "SAFE_TEST_MODE",
        "email_sent": False,
        "simulation_successful": True,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "message": "Email validated and simulated successfully. No real email was sent."
    }

def mark_execution_failed(execution_id: int, error_message: str):
    """
    Records execution failure using a fresh database session.
    """
    recovery_db = SessionLocal()

    try:
        failed_execution = recovery_db.query(ToolExecution).filter(
            ToolExecution.id == execution_id
        ).first()

        if failed_execution and failed_execution.status == "started":
            failed_execution.status = "failed"
            failed_execution.error_message = error_message
            failed_execution.completed_at = datetime.now(timezone.utc)

            recovery_db.commit()

    except Exception:
        recovery_db.rollback()
        raise

    finally:
        recovery_db.close()

# 4. EXECUTE AN APPROVED ACTION
@router.post("/execute/{approval_request_id}")
def execute_approved_action(
    approval_request_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # 1. Find the approval request belonging to this agent
    approval = db.query(ApprovalRequest).filter(
    ApprovalRequest.id == approval_request_id,
    ApprovalRequest.agent_id == agent.id
).first()

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found"
        )

    # Check whether the agent is active
    if agent.status.lower() != "active":
        raise HTTPException(
            status_code=403,
            detail="Agent is inactive and cannot execute actions"
        )

    # 2. Only approved requests can execute
    if approval.status.lower() != "approved":
        raise HTTPException(
            status_code=403,
            detail="Human approval is required before execution"
        )

    # 3. Check that this is the supported action
    if approval.action.lower() != "send_email":
        raise HTTPException(
            status_code=400,
            detail="This action is not supported for execution"
        )

    request_data = approval.request_data or {}

    # 4. Validate the resource
    if request_data.get("resource") != "email_service":
        raise HTTPException(
            status_code=400,
            detail="Invalid resource for Email Sender"
        )

    # 5. Check for a matching DENY policy again
    policies = db.query(SecurityPolicy).filter(
        SecurityPolicy.agent_id == agent.id,
        SecurityPolicy.is_enabled == True
    ).all()

    deny_policy = next(
        (
            policy for policy in policies
            if policy.effect.lower() == "deny"
            and policy.action.lower() in ["send_email", "*"]
            and (
                policy.resource is None
                or policy.resource.lower() in ["email_service", "*"]
            )
        ),
        None
    )

    if deny_policy:
        raise HTTPException(
            status_code=403,
            detail=f"Execution blocked by policy: {deny_policy.name}"
        )

    # 6. Find the active Email Sender tool
    tool = db.query(Tool).filter(
        Tool.name == "Email Sender",
        Tool.is_active == True
    ).first()

    if not tool:
        raise HTTPException(
            status_code=404,
            detail="Email Sender tool is unavailable"
        )

    # 7. Verify the agent's current tool permission
    assignment = db.query(AgentTool).filter(
        AgentTool.agent_id == agent.id,
        AgentTool.tool_id == tool.id
    ).first()

    if not assignment or assignment.permission.lower() != "allow":
        raise HTTPException(
            status_code=403,
            detail="Agent is not authorized to execute Email Sender"
        )

    # 8. Validate email information
    recipient = request_data.get("recipient")
    subject = request_data.get("subject")
    body = request_data.get("body")

    if not all(
        isinstance(value, str) and value.strip()
        for value in [recipient, subject, body]
    ):
        raise HTTPException(
            status_code=400,
            detail="Recipient, subject, and body are required"
        )

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        recipient.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid email recipient"
        )

    # 9. Create execution record before simulation.
    # The unique approval_request_id prevents duplicate executions.
    execution = ToolExecution(
        approval_request_id=approval.id,
        agent_id=agent.id,
        tool_id=tool.id,
        status="started"
    )

    db.add(execution)

    try:
        db.commit()
        db.refresh(execution)
        execution_id = execution.id
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This approval request has already been executed or execution was already started"
        )


    # 10. Simulate email execution
    try:
        result = simulate_email_send(
            recipient.strip(),
            subject.strip(),
            body.strip()
        )

    except Exception:
        # Simulation failed: recover using a fresh database session
         
        try:
            mark_execution_failed(
    execution_id,
    "Email simulation failed"
)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Email simulation failed"
        )

    # 11. Save successful execution and audit log
    try:
        execution.status = "success"
        execution.result = result
        execution.completed_at = datetime.now(timezone.utc)

        audit_entry = AuditLog(
            agent_id=agent.id,
            user_id=agent.owner_id,
            event_type="TOOL_EXECUTION",
            action=approval.action,
            resource="email_service",
            decision="SUCCESS",
            details={
                "approval_request_id": approval.id,
                "execution_id": execution.id,
                "execution_mode": "SAFE_TEST_MODE",
                "message": "Email simulation completed successfully"
            }
        )

        db.add(audit_entry)
        db.commit()
        db.refresh(execution)

        return {
            "message": "Approved action executed successfully",
            "execution_id": execution.id,
            "approval_request_id": approval.id,
            "agent_id": agent.id,
            "tool": tool.name,
            "status": execution.status,
            "result": execution.result
        }

    except Exception:
        db.rollback()

        try:
            mark_execution_failed(
                execution.id,
                "Execution result could not be saved to the database"
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Execution result could not be saved to the database"
        )


@router.get("/executions/{agent_id}")
def get_execution_history(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verify that the agent belongs to the logged-in user
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or access denied"
        )

    # 2. Fetch execution records with tool information
    executions = (
        db.query(ToolExecution, Tool.name)
        .join(Tool, ToolExecution.tool_id == Tool.id)
        .filter(ToolExecution.agent_id == agent.id)
        .order_by(ToolExecution.id.desc())
        .all()
    )

    # 3. Return execution history
    return [
        {
            "execution_id": execution.id,
            "approval_request_id": execution.approval_request_id,
            "agent_id": execution.agent_id,
            "tool_id": execution.tool_id,
            "tool_name": tool_name,
            "status": execution.status,
            "result": execution.result,
            "error_message": execution.error_message,
            "created_at": execution.created_at,
            "completed_at": execution.completed_at
        }
        for execution, tool_name in executions
    ]

# CHECK APPROVAL STATUS FOR AN AGENT
@router.get("/approval-requests/{request_id}/status")
def check_approval_status(
    request_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # 1. Find the approval request belonging to this agent
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id,
        ApprovalRequest.agent_id == agent.id
    ).first()

    # 2. Check whether the request exists
    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found"
        )

    # 3. Return the current approval status
    return {
        "approval_request_id": approval.id,
        "agent_id": approval.agent_id,
        "action": approval.action,
        "status": approval.status,
        "reason": approval.reason,
        "reviewed_at": approval.reviewed_at
    }
