
from langchain_core.tools import tool
from app.services.langchain_guard import AgentGuardTool


# Original email tool (simulation only)
@tool
def email_sender(
    recipient: str,
    subject: str,
    body: str
) -> str:
    """Simulates sending an email."""

    print("ORIGINAL EMAIL TOOL EXECUTED!")

    return (
        f"Email simulation completed for {recipient}"
    )


# Protect the email tool with AgentGuard
protected_email_tool = AgentGuardTool(
    name="Email Sender",
    description="An email tool protected by AgentGuard.",
    wrapped_tool=email_sender,
    args_schema=email_sender.args_schema,
    agent_api_key="ozaarREmGDtMnXfPEN29ReOkxuUd_oiBWObniDno4GM",
    action="send_email",
    resource="email_service"
)


# Test the protected email action
try:
    result = protected_email_tool.invoke({
        "recipient": "customer@example.com",
        "subject": "AgentGuard Approval Test",
        "body": "Testing structured email approval."
    })

    print("Tool result:", result)

except Exception as error:
    print("AgentGuard stopped the action:")
    print(error)
